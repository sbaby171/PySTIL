import re
import STILutils as sutils
import SymbolTable as STBL
import KeyLookUps as KL





class PatternBurstBlocks(object): 
    def __init__(self): 
        self.patternBursts = {} # Name -> PatternBurstObject
    def add(self, patternBurst): 
        if not isinstance(patternBurst, PatternBurst): 
            raise ValueError("Must provide instance of PatternBurst.")
        self.patternBursts[patternBurst.name] = patternBurst
    def get(self, name): 
        if name in self.patternBursts: return self.patternBursts[name]
        else: return None
    def __len__(self): 
        return len(self.patternBursts)

class PatternBurst(object):
    def __init__(self, name=""):
        # TODO: Error if empty?  
        self.name = name 

        self.patLists = []
        self.patSets  = []
        self.parallelPatLists = []
    
    def add(self, entity): 
        if isinstance(entity, PatList): 
            self.parallelPatLists.append(entity)
        elif isinstance(entity, ParallelPatList): 
            self.patLists.append(entity)
        elif isinstance(entity, PatSet): 
            self.patSets.append(entity)
        else: 
            raise RuntimeError("Must provide instance of either "\
                "PatList, ParallelPatList, or PatSet.")
        



    #def add(self, entity): 
    #    if isinstance(entity, Category): 
    #        if entity.name in self.categories: 
    #            raise RuntimeError("Category (%s) is already defined."%(entity.name))
    #        else: self.categories[entity.name] = entity
    #    elif isinstance(entity, Variable): 
    #        if entity.name in self.variables: 
    #            raise RuntimeError("Variable (%s) is already defined."%(entity.name))
    #        else: self.variables[entity.name] = entity
    #    else: 
    #        raise ValueError("Entity is of to be classes 'Category' or 'Variable'.")

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

    if "ParallelPatList" in sytbl:
        print("Contains ParrallelPatList") 

    # ParallelPatList: 
    for i in sytbl["ParallelPatList"]: 
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

        pat = ""
        cbcount = 0 
        while j <= jend: 
            token = tokens[j]['token']
            tag   = tokens[j]['tag'] 
            
            # State dependent: 
            if inPattern: 
                if tag == "}": cbcount -= 1
                if cbcount == 0: 
                    inPattern = 0; j+=1; continue 
                if tag == "Extend": 
                    ppl[pat]["Extend"] = True
                    #ppl.extend(pat)
                    if tokens[j+1]['tag'] != ';': 
                        raise RuntimeError("Expecting ';' after Extend statment.")

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
