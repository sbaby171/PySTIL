#!/usr/bin/env python
import os
import time
import re
from collections import OrderedDict
import funcs
# ============================================================================:
# Stages of Compiler: 
# -PySTIL/compiler.py::PySTIL.compiler.read() 
# TLBs = Top-Level-Blocks
# 
# NOTES: by default we ignore the ScanStructures. We will locate their 
# starting lines but will NEVER parse unless explictily asked.
#
# NOTE: There is an optimization f
#
# 1.) Pre-processing: Locate line-numbers for all TLBs
#     - Locate all the PatternExec blocks. If multiple, user must indicate 
#       which one to use? If not defined, we defatul to the GLOBAL-DOMAIN. 
#     - From this PatternExec block we pull all pieces (expect patterns)
#       al parse them out. 
#     - NOTE: There is an optimzation to skip skip all Pattern searching after
#       the first one is found. This is going to be set as default
#     Q: Whate the implication from the PatternExec? I seeing only two 
#     references: Timing and PatternBurst
# 
# ============================================================================:
class STIL(object): 
    def __init__(self,*args,**kwargs): 
        self.signals = None 
        if "signals" in kwargs: self.signals = kwargs["signals"]
        self.filepath = "" 
        if "filepath" in kwargs: self.filepath = kwargs["filepath"]

    def get_signals(self,): 
        return self.signals 
# ============================================================================:
# Q: What is a valid syntax for a signal name: 
# - SIG_NAME See 6.10 in 1450.0
#   data[0..36] -> data[0], data[1], ..., data[35], data[36]
#   "a&b"[0..7] -> "a&b"[0], "a&b"[1], ..., "a&b"[6], "a&b"[7]
#   The brackets, when present, become pat of the name reference, and the 
#   the values inside of the braket are interpreted as integer values only
#   -> data[0] === data[00] != data00
#   Ascending ([0..7]) or descending ([7..0]) are allowed. 
#class Signals(OrderedDict): 
#    def __init__(self,name):
#        super(Signals,self).__init__()
#        self.name = name  
#    def __setitem__(self,name,value): 
#        self[name] = value
class Signals(object): 
    def __init__(self,name):
        #super(Signals,self).__init__()
        self.name = name  
        self._odict = OrderedDict()
        self._expansion = {} 
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
# ============================================================================:
def build_Signals(tokens): 
    func = "build_Signals"
    typelist = set(["In","Out","InOut","Supply","Psuedo"])
 
    domain = funcs.references.GLOBAL_DOMAIN
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
            else: raise RuntimeError("bad")
        # --------------------------------------------------------------------:
        i+=1 
    return SG
# ============================================================================:
class SignalGroups(object): 
    def __init__(self,name,): 
        self.name = name 
        self._dict = OrderedDict()
        self._expr = OrderedDict() # Holds raw expression for read

    def add_expr(self,name,expression):
        self._expr[name] = expression 
# ============================================================================:
def build_SignalGroups(tokens): 
    func = "build_SignalGroups"
    domain = funcs.references.GLOBAL_DOMAIN
    if tokens[0]["token"] != "SignalGroups": 
        raise RuntimeError("First SignalGroups token is not 'SignalGroups'")
    fi = -1 
    if tokens[1]["tag"] == "identifier": 
        domain = tokens[1]["token"]
        if tokens[2]["token"] != "{": 
            raise RuntimeError("First SignalGroups token is not 'SignalGroups'")
        fi = 3
    elif tokens[1]["tag"] == "{": fi = 2 
    else: raise RuntimeError("Issue with SignalGroups tokens: %s"%(tokens))

    sg = SignalGroups(domain)
    if fi == -1: raise RuntimeError("fi is off")
    i = fi; end = len(tokens)-1; cbs = 1; 
    while i <= end: 
        # EXIT----------------------------------------------------------------:
        if tokens[i]["token"] == "}": 
            cbs -= 1; 
            if cbs == 0: break 
        # --------------------------------------------------------------------:
        if tokens[i]['tag'] == "identifier": 
            if tokens[i+1]['tag'] != "=": 
                print("ERROR:     i = %s, %s"%(i,tokens[i]))
                print("ERROR: 1 + i = %s, %s"%(i+1,tokens[i+1]))
                raise RuntimeError("need '=' after identifier")
            j = i 
            while j < end:
                if tokens[j]['tag'] == ";": 
                    n = tokens[i]["token"]
                    e = "".join([tokens[k]["token"] for k in range(i+2,j+1)])
                    print("DEBUG: [%s]: Adding: %s = %s"%(func,n,e))
                    sg.add_expr(n,e)
                    i = j; break
                j += 1
                if j == end:raise RuntimeError("bad")
        # --------------------------------------------------------------------:
        i += 1
    return sg 
# ============================================================================:
# TODO: If the Signal and SignalGroups block do not have to be referenced 
# by the PatternExec or Timing, then how/where is it selected if there are more
# than one? 
#   - "Only one Signals block is allowed in a STIL file set; any other Siganl
#     block  parsed is ignored. This is to facilitate the collection of 
#     several separate STIL programs for a DUT into a complete test" - 1450 
#     Section 14. "Signals block". To me, this means all other after the 
#     the first are to be ignored. (tlbs["Signals"][0])
class PatternExec(object): 
    def __init__(self,name,category="",selector="",
                 timing="",patternBurst="",dcLevels="", dcSets=""): 
        self.name = name 
        self.category = category
        self.selector = selector
        self.timing = timing
        self.patternBurst = patternBurst
        self.dcLevels = dcLevels # 1450.2
        self.dcSets = dcSets     # 1450.2
# ============================================================================:
def build_PatternExec(tokens): 
    domain = funcs.references.GLOBAL_DOMAIN
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
    while i <= end: 
        # EXIT----------------------------------------------------------------:
        if tokens[i]["token"] == "}": 
            cbs -= 1; 
            if cbs == 0: break 
        # --------------------------------------------------------------------:
        if tokens[i]["tag"] == "Timing": 
            if ((tokens[i+1]["tag"] != "identifier") or 
               (tokens[i+2]["tag"] != ";")):
                raise RuntimeError("Bad Timing reference")
            PE.timing = tokens[i+1]["token"]
            i += 3; continue 
        # --------------------------------------------------------------------:
        if tokens[i]["tag"] == "PatternBurst": 
            if ((tokens[i+1]["tag"] != "identifier") or 
               (tokens[i+2]["tag"] != ";")):
                raise RuntimeError("Bad PatternBurst reference")
            PE.patternBurst = tokens[i+1]["token"]
            i += 3; continue 
        # --------------------------------------------------------------------:
        i += 1
    return PE
# ============================================================================:
def read(sf,allow_fullbreak=True,debug=False): 
    func = "PySTIL.stil.read"
    if not os.path.isfile(sf): 
        raise ValueError("Provide STIL file doesn't exist or has restrictive"\
           " permissions: %s"%(sf))
    print("DEBUG: [%s]: Received: %s"%(func,sf))
    TLBs = list(funcs.references.TOP_LEVEL_KEYWORDS)
    # ========================================================================:
    # (1) First Pass 
    # The first pass makes the assumption the the TOP-LEVEL block with start
    # on its own line; in that it will be the first identifier on a line. 
    # 
    # On first pass, we should becareful to only grab TOP-level blocks. This 
    # emphasis is becasue some top-level blocks can also be found within other
    # blocks. For example, the "Ann" block can be found within other blocks. 
    # 
    # Note, there are optimzations that could be made: 
    #  - popping certain TLB from search list, once they are found. 
    #  - once PatternExec block found, limit the TLB search -> if Pattern TLB
    #    only search Pattern blocks. 
    # ^^^ Much of this optmizations need to be verified, if employed, against
    #     many STILs and against the standard specifications. 
    tlbs = OrderedDict() 
    tlbs["PatternExec"] = [] # TODO: Add other blocks ? 
    tlbs["Signals"] = [] # TODO: Add other blocks ? 
    tlbs["SignalGroups"] = [] # TODO: Add other blocks ? 
    # ^^^^ NOTE: We are pre-loading some important blocks that we are 
    # expecting to check regardless of what user configures .
    tlls = [] # To hold all starting line keys
    Stil = STIL()
    stilIndex = {1:sf} # NOTE: Include files will add to this. 
    ptS = time.time()
    fullbreak = False 
    for ln,line in funcs._read_line(sf): 
        if not line: continue 
        if line.startswith("//"): continue
        if fullbreak: 
            if allow_fullbreak: ln = -1; break;
            else: fullbreak = False 
        for kw in TLBs: # Moved out refs.TOP_LEVEL for optimzations
            if re.match("^%s\s|$|{"%(kw),line): 
                domain = funcs.get_domain_name(line,kw)
                if kw not in tlbs: tlbs[kw] = []
                tlbs[kw].append({"line-count":ln,
                                 "source-file":1,"domain":domain})
                tlls.append(int(ln))
                #if kw == "Pattern": TLBs = set(["Pattern"]) # NOTE
                if kw == "Pattern": 
                    if allow_fullbreak: fullbreak = True
                    else: TLBs = set(["Pattern"])
                break
    ptE = time.time()
    funcs.report_filesize_and_processing(ptS,ptE,ln,sf,debug=debug)
    # (1) first pass over
    for index, stil in stilIndex.items(): 
        print("%d.)  %s"%(index,stil))
    for kw,instances in tlbs.items(): 
        print(kw + ": ")
        for instance in instances: 
            print("- %s"%(instance))
    print("Top-level-lines: %s"%(tlls))
    # -----------------------------------------------------------------------:
    # NOTE: at this point, we have grabbed all the top-level tags, However, 
    # there will be false top-level tags due to references within blocks to 
    # other blocks. In some stils, I see 
    # -----------------------------------------------------------------------: 
    # TODO: Technically, there can be multiple PatternExec blocks per STIL. 
    # so we should not fail if more than one, also, we should be more careful
    # for removing instances based after  
    #if len(tlbs["PatternExec"]) > 1: 
    #    raise RuntimeError("Found more than 1 PatternExec block")
    if tlbs["PatternExec"].__len__() >= 1: 
        lnPatternExec = tlbs["PatternExec"][0]["line-count"]
        for kw, instances in tlbs.items(): 
            if instances.__len__() > 1: 
                #print("Multiple instances of %s"%(kw))
                for i,instance in enumerate(instances): 
                    if instance["line-count"] > lnPatternExec: 
                        #print("Not top-level instance: %s"%(instance))
                        del tlls[tlls.index(instance["line-count"])]
                        del tlbs[kw][i] # Remove instance
        print("DEBUG: [%s]: Top-level-blocks, line instances:"%(func))
        for kw,instances in tlbs.items(): # Debug show the new TLBs
            print("DEBUG: [%s]: %s"%(func,kw))
            for instance in instances: 
                print("DEBUG: [%s]  - %s"%(func,instance))
        print("DEBUG: [%s]: Top-level-lines: %s"%(func,tlls))
    # -----------------------------------------------------------------------:
    # Parse the PatternExec block TODO: need lexer
    if tlbs["PatternExec"].__len__() >= 1: 
        lnS = tlbs["PatternExec"][0]["line-count"]
        try:    lnE = tlls[tlls.index(lnS) + 1] - 1
        except: lnE = 0
        pxlines = [line for ln,line in funcs._read_line_range(sf,lnS, lnE)]
        pxtokens = funcs.lex(pxlines)
        patternExec = build_PatternExec(pxtokens)
        print(patternExec)
        print(patternExec.name)
        print(patternExec.timing)
        print(patternExec.patternBurst)
        Stil.patternExec = patternExec
    # -----------------------------------------------------------------------:
    # Parse the Signals block
    if tlbs["Signals"].__len__() >= 1: 
        lnS = tlbs["Signals"][0]["line-count"]
        try:    lnE = tlls[tlls.index(lnS) + 1] - 1
        except: lnE = 0
        sglines = [line for ln,line in funcs._read_line_range(sf,lnS,lnE)]
        sgtokens = funcs.lex(sglines)
        signals = build_Signals(sgtokens)
        print(signals)
        print(signals.name)
        print(signals.__len__())
        Stil.signals = signals 
    # -----------------------------------------------------------------------:
    # Parse the SignalGroups
    if tlbs["SignalGroups"].__len__() >= 1: 
        lnS = tlbs["SignalGroups"][0]["line-count"]
        try:    lnE = tlls[tlls.index(lnS) + 1] - 1
        except: lnE = 0 
        sglines = [line for ln,line in funcs._read_line_range(sf,lnS,lnE)]
        sgtokens = funcs.lex(sglines)
        for tk in sgtokens: print(tk)
        sg = build_SignalGroups(sgtokens)
        print(sg.name)
        for n,e in sg._expr.items(): print(n,e)
        Stil.signalGroups = sg
    print("DEBUG: All first pass activities done")
    # ========================================================================:
    # (2) Second pass: 
    #tlbs["Signals"]
    #for sb in tlbs["Signals"]: 
    #    if sb["domain"] == funcs.references.GLOBAL_DOMAIN:
    #        start = sb["line-count"]
    #        end   = tlls[tlls.index(start) + 1] 
    #        print(start,end)
    return Stil
# ----------------------------------------------------------------------------:
