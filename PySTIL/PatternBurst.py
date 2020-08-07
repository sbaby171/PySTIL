import re
import STILutils as sutils
import SymbolTable as STBL
import KeyLookUps as KL



class PatternBurstBlocks(sutils.Blocks): 
    def __init__(self): 
        super().__init__()
    def add(self, patternBurst): 
        super().add(patternBurst, PatternBurst)

class PatternBurst(object):
    def __init__(self, name):
        self.name = name 
        self.blocks = {"PatList": [], "ParallelPatList":[], "PatSet":[]}
        self.ordering = [] # [(type,index)]
    
    def add(self, entity): 
        if isinstance(entity, PatList): 
            self.blocks["PatList"].append(entity)
            self.ordering.append(("PatList",len(self.blocks["PatList"])-1))
        elif isinstance(entity, ParallelPatList): 
            self.blocks["ParallelPatlist"].append(entity)
            self.ordering.append(("ParallelPatList",len(self.blocks["ParallelPatList"])-1))
        elif isinstance(entity, PatSet): 
            self.blocks["PatSet"].append(entity)
            self.ordering.append(("PatSet",len(self.blocks["PatSet"])-1))
        else: 
            raise RuntimeError("Must provide instance of either "\
                "PatList, ParallelPatList, or PatSet.")

def create_PatternBurst(string, name = "", file = "", debug=False):
    """ 
    String is a raw string. Typically this will be coming from the 
    STIL object. 
    """
    func   = "create_PatternBurst"
    tokens = sutils.lex(string=string, debug=debug)
    sytbl  = STBL.SymbolTable(tokens=tokens, debug=debug) 
    pb     = PatternBurst(name=name)
    if debug: 
        print("DEBUG: (%s): Tokens: %s "% (func, tokens))
        print("DEBUG: (%s): SymbolTable: %s"%(func, sytbl))
    
    # TODO: Keep order of the PatList, ParallelPatList, PatSet
    tmap = {} 
    for i in sytbl["PatList"]: tmap[i] = "PatList"
    for i in sytbl["ParallelPatList"]: tmap[i] = "ParallelPatList"
    for i in sytbl["PatSet"]: tmap[i] = "PatSet"

    todos = []
    [todos.append((key,value)) for (key, value) in sorted(tmap.items())]
    for todo in todos: 
        i = todo[0]; block = todo[1]
        if block == "ParallelPatList": 
            cbs, cbe = sytbl.get_next_curly_set(i)
            ppl = ParallelPatList()
            # Handle ParallelPatList Mode.
            if cbs - i == 2: 
                if tokens[i+1]['tag'] not in ParallelPatList.modes: 
                    raise RuntimeError("ParallelPatList must be of modes"\
                    "%s. Recieved the following: %s"%(ParallelPatList.modes, tokens[i+1]['token']))
                else: ppl.mode = tokens[i+1]['tag']
            print(ppl.mode)

            j = cbs + 1; jend = cbe - 1 
            # State flags: 
            inPattern = False
            inSignalGroups = False 
            inMacroDefs = False 
            inProcedures = False 
            inScanStructures = False 
            inStart = False; inStop = False
            inTermination = False 

            pat = ""; cbcount = 0 
            while j <= jend: 
                token = tokens[j]['token']
                tag   = tokens[j]['tag'] 
                # State dependent: 
                if inPattern: 
                    if tag == "}": cbcount -= 1
                    if cbcount == 0: inPattern = 0; j+=1; continue 
                    if tag == "Extend": 
                        ppl[pat]["Extend"] = True
                        if tokens[j+1]['tag'] != ';': 
                            raise RuntimeError("Expecting ';' after Extend statment.")
                        # TODO: if tag == "SignalGroups", etc.
                    j+=1; continue 

                # Freelance: 
                if tag == 'identifier': 
                    pat = token; ppl.add(token)
                    if tokens[j+1]['tag'] == ";": 
                        j += 2; continue 
                    elif tokens[j+1]['tag'] == "{":
                        cbcount = 1 
                        inPattern = True
                        j += 2; continue 
                    else: raise RuntimeError("Expecting Pattern name.")
                j += 1
            print(ppl.patterns)
            pb.add(ppl)    
    return pb



class PatList(object): 
    def __init__(self, ): 
        self.patterns = {} # name -> {}
        # SignalGroups, MacrosDefs, etc. 

    def add(self, patname): 
        if patname in self.patterns: 
            raise RuntimeError("Pattern is already named:  %s"%(patname))
        self.patterns[patname] = {}
    
    def __getitem__(self, pattern): 
        if pattern in self.patterns: return self.patterns[pattern] 
        else: return None 

class ParallelPatList(PatList): 
    modes = ["SyncStart", "Independent", "LockStep"]

    def __init__(self,): 
        super().__init__()
        self.mode = 'Independent'

    def extend(self, pattern): 
        if pattern not in self.patterns: 
            raise RuntimeError("No pattern by the name is defined: %s"%(pattern))
        else: self.patterns[pattern]['Extend'] = True

class PatSet(PatList): 
    def __init__(self,): 
        super().__init__()
