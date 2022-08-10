from collections import OrderedDict
import STILFuncs as SF
# ============================================================================:
class STIL(object): 
    def __init__(self,*args,**kwargs): 
        self.signals = None 
        if "signals" in kwargs: self.signals = kwargs["signals"]
        self.filepath = "" 
        if "filepath" in kwargs: self.filepath = kwargs["filepath"]
        self.signalGroups = None 
        if "signalGroups" in kwargs: self.signalGroups = kwargs["signalGroup"]

    def get_Signals(self,): 
        return self.signals 
    def get_SignalGroups(self,): 
        return self.signalGroups 
# TODO: How to accomidate multiple Blocks but only one main block. 
# ============================================================================:
# ============================================================================:
class Signals(object): 
    def __init__(self,filepath="",name=""):
        self.name = name  
        self._filepath = filepath  
        self._odict = OrderedDict() # signals as shown in stil
        self._expansion = {}  # expanded signals within Signals shorthand
    def __setitem__(self,name,value): 
        if ".." in name: 
            bn = name.split("[")[0] # basename
            num1 = int(name.split("..")[0].split("[")[-1])
            num2 = int(name.split("..")[-1].split("]")[0])
            if num1 > num2: low = num2; high = num1
            else: high = num2; low = num1
            names = ["%s[%d]"%(bn,j) for j in range(low,high+1)]
            self._expansion[name] = set(names)
        self._odict[name] = value
    def __getitem__(self,name): 
        return self._odict[name]
    def __len__(self): 
        length = len(self._odict) - len(self._expansion)
        for e,names in self._expansion.items(): 
            length += len(names)
        return length
    def __contains__(self,name): 
        if name in self._odict: return True 
        if name in self._expansion: return True
        return False 
    def get_signals(self,): 
        return list(self._odict.keys())
# ----------------------------------------------------------------------------:
def build_Signals(tokens): 
    func = "build_Signals"
    typelist = set(["In","Out","InOut","Supply","Psuedo"])
 
    domain = SF.references.GLOBAL_DOMAIN
    if tokens[0]["token"] != "Signals": 
        raise RuntimeError("First Signals token is not 'Signals'")
    fi = -1 
    if tokens[1]["tag"] == "identifier": 
        domain = tokens[1]["token"]
        if tokens[2]["token"] != "{": 
            raise RuntimeError("First Signals token is not 'Signals'")
        fi = 3
    elif tokens[1]["tag"] == "{": fi = 2 
    else: raise RuntimeError("Issue with Signals tokens: %s"%(tokens))
    if fi == -1: raise RuntimeError("fi is off")
    SG = Signals(domain)
    i = fi; end = len(tokens)-1; cbs = 1; 
    while i <= end: 
        # EXIT----------------------------------------------------------------:
        if tokens[i]["token"] == "}": 
            cbs -= 1; 
            if cbs == 0: break 
        # --------------------------------------------------------------------:
        if tokens[i]["tag"] == "identifier":  # NOTE" Simple defintion
            if tokens[i+2]["tag"] == ";": 
                if tokens[i+1]['tag'] in typelist: 
                    sname = tokens[i]["token"]
                    stype = tokens[i+1]["tag"]
                    #print("DEBUG: [%s]: Adding Signal '%s'"%(func,sname))
                    SG[sname] = {"type":stype}  
                    # add 
                    i += 3; continue 
                else: raise RuntimeError("Bad")
            elif tokens[i+2]["tag"] == "{":
                print("TODO")
            else:
                print("ERROR:     i = %s, %s"%(i,tokens[i]))
                print("ERROR: 1 + i = %s, %s"%(i+1,tokens[i+1]))
                print("ERROR: 2 + i = %s, %s"%(i+2,tokens[i+2]))
                raise RuntimeError("bad")
        # --------------------------------------------------------------------:
        i+=1 
    return SG
# ============================================================================:

class SignalGroups: 
    def __init__(self,): 
        pass 

class Timing: 
    def __init__(self,): 
        pass 
# ============================================================================:
class PatternExec(object): 
    def __init__(self,name,category="",selector="",timing="",
                 patternBurst="",dcLevels="", dcSets=""): 
        self.name = name 
        self.category = category
        self.selector = selector
        self.timing = timing
        self.patternBurst = patternBurst
        self.dcLevels = dcLevels # 1450.2
        self.dcSets = dcSets     # 1450.2

    def __str__(self,): 
        rstr = [] 
        if self.name == SF.references.GLOBAL_DOMAIN: 
            rstr.append("PatternExec {")
        else: rstr.append("PatternExec %s {"%(self.name))
        if self.category: rstr.append("  Category %s;"%(self.category))
        if self.selector: rstr.append("  Selector %s;"%(self.selector))
        if self.dcLevels: rstr.append("  DCLevels %s;"%(self.dcLevels))
        if self.dcSets:   rstr.append("  DCSets %s;"%(self.dcSets))
        if self.timing:   rstr.append("  Timing %s;"%(self.timing))
        if self.patternBurst: 
            rstr.append("  PatternBurst %s;"%(self.patternBurst))
        rstr.append("}")
        return "\n".join(rstr)

def build_PatternExec(tokens): 
    domain = SF.references.GLOBAL_DOMAIN
    if tokens[0]["token"] != "PatternExec": 
        raise RuntimeError("First PatternExec token is not 'PatternExec'")
    fi = -1 
    if tokens[1]["tag"] == "identifier": 
        domain = tokens[1]["token"]
        if tokens[2]["token"] != "{": 
            raise RuntimeError("First PatternExec token is not 'PatternExec'")
        fi = 3
    elif tokens[1]["tag"] == "{": fi = 2 
    else: raise RuntimeError("Issue with PattenExec tokens: %s"%(tokens))

    PE = PatternExec(domain)
    if fi == -1: raise RuntimeError("fi is off")
    i = fi; end = len(tokens)-1; cbs = 1; 
    kws = set(["Category","Selector","Timing","PatternBurst",
               "DCLevels","DCSets"])
    while i <= end: 
        # EXIT----------------------------------------------------------------:
        if tokens[i]["tag"] == "}": 
            cbs -= 1; 
            if cbs == 0: break 
        # --------------------------------------------------------------------:
        if tokens[i]["tag"] in kws: 
            if ((tokens[i+1]["tag"] != "identifier") or 
               (tokens[i+2]["tag"] != ";")):
                raise RuntimeError("Bad keyword reference")
            kw = tokens[i]['tag']
            if   kw == "Category":     PE.category = kw
            elif kw == "Selector":     PE.selector = kw
            elif kw == "Timing":       PE.timing = kw
            elif kw == "DCLevels":     PE.dcLevels = kw
            elif kw == "DCSets":       PE.dcSets = kw
            elif kw == "PatternBurst": PE.patternBurst = kw
            i += 3; continue 
        # --------------------------------------------------------------------:
        i += 1
    return PE
# ============================================================================:

class Pattern: 
    def __init__(self,): 
        pass 
