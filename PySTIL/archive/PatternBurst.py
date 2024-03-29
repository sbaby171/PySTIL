import sys, re
from collections import OrderedDict
import STILutils as sutils
import SymbolTable as STBL
import KeyLookUps as KL



class PatternBurstBlocks(sutils.Blocks): 
    def __init__(self): 
        super(PatternBurstBlocks, self).__init__()
    def add(self, patternBurst): 
        super(PatternBurstBlocks, self).add(patternBurst, PatternBurst)
    
     

class PatternBurst(object):
    def __init__(self, name, file=""):
        self.name = name 
        self.file = file
        self.blocks = {"PatList": [], "ParallelPatList":[], "PatSet":[]}
        self.ordering = [] # [(type,index)]

        self.SignalGroups = None 
        self.MacroDefs = None 
        self.Procedures = None 
        self.ScanStructures = None 
        self.Start = None 
        self.Stop = None 
        self.Termination = None 
    
    def get_name(self,): return self.name 
    def get_file(self,): return self.file
    
    def add(self, entity): 

        if isinstance(entity, ParallelPatList): 
            self.blocks["ParallelPatList"].append(entity)
            self.ordering.append(("ParallelPatList",len(self.blocks["ParallelPatList"])-1))
        elif isinstance(entity, PatSet): 
            self.blocks["PatSet"].append(entity)
            self.ordering.append(("PatSet",len(self.blocks["PatSet"])-1))
        elif isinstance(entity, PatList): 
            self.blocks["PatList"].append(entity)
            self.ordering.append(("PatList",len(self.blocks["PatList"])-1))
        else: 
            raise RuntimeError("Must provide instance of either "\
                "PatList, ParallelPatList, or PatSet.")
    
    def patterns(self, ):
        """Return list of all patterns referenced in PatternBurst block."""
        retlist = []
        for subblock in self.blocks: 
            for instance in self.blocks[subblock]:
                retlist.extend(instance.patterns.keys())
        return retlist
    
    def get_PatLists(self,): 
        """Returns a list of PatList objects. Note, STIL does not allow 
        for naming of PatList blocks. Thus, we must always return a list."""
        return self.blocks["PatList"]
    def get_PatSets(self,): 
        """Returns a list of PatSet objects. Note, STIL does not allow 
        for naming of PatSet blocks. Thus, we must always return a list."""
        return self.blocks["PatSet"]
    def get_ParallelPatLists(self,): 
        """Returns a list of ParallelPatList objects. Note, STIL does not allow 
        for naming of ParallelPatList blocks. Thus, we must always return a list."""
        return self.blocks["ParallelPatList"]

def create_PatternBurst(string, name = "", file = "", debug=False):
    """ 
    String is a raw string. Typically this will be coming from the 
    STIL object. 
    """
    func   = "create_PatternBurst"
    tokens = sutils.lex(string=string, debug=debug)
    sytbl  = STBL.SymbolTable(tokens=tokens, debug=debug) 
    pb     = PatternBurst(name=name, file=file)

    if debug: 
        print("DEBUG: (%s): Tokens:"% (func))
        for i, token in enumerate(tokens,start=0): 
            print("DEBUG: (%s): %d: %s"%(func,i,token))

        print("DEBUG: (%s): SymbolTable: %s"%(func, sytbl))
    
    # Parse over the outside layers first: 
    pbi = sytbl["PatternBurst"][0]
    if tokens[pbi + 1]['tag'] != 'identifier': 
        raise RuntimeError("Expecting identifier after 'PatternBurst'")
    if tokens[pbi + 2]['tag'] != '{': 
        raise RuntimeError("Expecting '{' to start 'PatternBurst' defintiion.")

    # Process everything outside of ParallelPatList, PatList, and PatSet
    cbs, cbe = sytbl.get_next_curly_set(pbi)
    i = cbs + 1; iend = cbe - 1
    while i <= iend: 
        # Jump over all internal blocks: 
        if tokens[i]['tag'] in ["PatList","PatSet","ParallelPatList"]: 
            _cbs, _cbe = sytbl.get_next_curly_set(i)
            i = _cbe; continue 
        # Handle PatternBurst Settings: 
        if tokens[i]['tag'] == "SignalGroups": 
            if tokens[i+1]['tag'] != 'identifier': 
                raise RuntimeError("Expecting identifier after SignalGroups.")
            if tokens[i+2]['tag'] != ';': 
                raise RuntimeError("Expecting SignalGroups to be terinated by ';'.")
            pb.SignalGroups = tokens[i+1]['token']
            i += 3; continue 
        # TODO: Do others .....
        i += 1; continue 

    # TODO: Keep order of the PatList, ParallelPatList, PatSet
    tmap = {} 
    for i in sytbl["PatList"]: tmap[i] = "PatList"
    for i in sytbl["ParallelPatList"]: tmap[i] = "ParallelPatList"
    for i in sytbl["PatSet"]: tmap[i] = "PatSet"
    todos = []
    [todos.append((key,value)) for (key, value) in sorted(tmap.items())]
    for todo in todos: 
        i = todo[0]; block = todo[1]
        if   block == "PatList": spb = PatList()
        elif block == "PatSet": spb = PatSet()
        elif block == "ParallelPatList": spb = ParallelPatList() 
        else: RuntimeError("Expecting PatList, PatSet, or ParallelPatList.")
        # Establish flags used for parsing
        inPattern = False
        inPatternStart = None; inPatternEnd = None
        patname = ""
        # get block start and ends, 
        cbs , cbe = sytbl.get_next_curly_set(i)
        j = cbs + 1; jend = cbe - 1
        while j <= jend: 
            if inPattern: 
                if j == inPatternEnd: 
                    inPattern = False 
                    inPatternStart = None 
                    inPatternEnd = None
                    patname = ""
                    j += 1; continue 
                # Adding fields: 
                if tokens[j]['tag'] == 'Extend': 
                    spb.add_field(patname, 'Extend', True)
                    if tokens[j+1]['tag'] != ';': 
                        raise RuntimeError("Expecting semicolon after Extend")
                    j+=2; continue
                if tokens[j]['tag'] == 'Start':  
                    if tokens[j+1]['tag'] == 'identifier': 
                        spb.add_field(patname, 'Start', tokens[j+1]['token'])
                        if tokens[j+2]['tag'] != ';': 
                            raise RuntimeError("Expecting semicolon after Start.")
                    else: raise RuntimeError("Expecting identifier after Start.")
                    j+=3; continue
                if tokens[j]['tag'] == 'Stop':  
                    if tokens[j+1]['tag'] == 'identifier': 
                        spb.add_field(patname, 'Stop', tokens[j+1]['token'])
                        if tokens[j+2]['tag'] != ';': 
                            raise RuntimeError("Expecting semicolon after Stop.")
                    else: raise RuntimeError("Expecting identifier after Stop.")
                    j+=3; continue
                if tokens[j]['tag'] == 'SignalGroups': # TODO: I think you can multiple instances, acording to 17.1 1405.0 
                    if tokens[j+1]['tag'] == 'identifier': 
                        spb.add_field(patname, 'SignalGroups', tokens[j+1]['token'])
                        if tokens[j+2]['tag'] != ';': 
                            raise RuntimeError("Expecting semicolon after SignalGroups.")
                    else: raise RuntimeError("Expecting identifier after SignalGroups.")
                    j+=3; continue
                if tokens[j]['tag'] == 'MacroDefs': # TODO: I think you can multiple instances, acording to 17.1 1405.0 
                    if tokens[j+1]['tag'] == 'identifier': 
                        spb.add_field(patname, 'MacroDefs', tokens[j+1]['token'])
                        if tokens[j+2]['tag'] != ';': 
                            raise RuntimeError("Expecting semicolon after MacroDefs.")
                    else: raise RuntimeError("Expecting identifier after MacroDefs.")
                    j+=3; continue
                if tokens[j]['tag'] == 'Procedures': # TODO: I think you can multiple instances, acording to 17.1 1405.0 
                    if tokens[j+1]['tag'] == 'identifier': 
                        spb.add_field(patname, 'Procedures', tokens[j+1]['token'])
                        if tokens[j+2]['tag'] != ';': 
                            raise RuntimeError("Expecting semicolon after Procedures.")
                    else: raise RuntimeError("Expecting identifier after Procedures.")
                    j+=3; continue
                if tokens[j]['tag'] == 'ScanStructures': # TODO: I think you can multiple instances, acording to 17.1 1405.0 
                    if tokens[j+1]['tag'] == 'identifier': 
                        spb.add_field(patname, 'ScanStructures', tokens[j+1]['token'])
                        if tokens[j+2]['tag'] != ';': 
                            raise RuntimeError("Expecting semicolon after ScanStructures.")
                    else: raise RuntimeError("Expecting identifier after ScanStructures.")
                    j+=3; continue
                # TODO: Termination....
                j += 1; continue 
            if tokens[j]['tag'] in ['SyncStart','Independent','LockStep']: 
                spb.mode = tokens[j]['token'] 
                j += 1; continue 

            if tokens[j]['tag'] == 'Ann': 
                j = sytbl.get_next_instance(tag='*}',startIndex=j)
                continue 


            if tokens[j]['tag'] == 'identifier': 
                patname = tokens[j]['token'] 
                spb.add_pattern(patname)
                if debug: print("DEBUG: (%s): Added Pattern: %s"%(func, patname))
                if tokens[j+1]['tag'] == ';': 
                    j += 2; continue 
                elif tokens[j+1]['tag'] == "{": 
                    inPattern = True
                    inPatternStart, inPatternEnd = sytbl.get_next_curly_set(j)
                    j = inPatternStart + 1; continue 
            j += 1 
        pb.add(spb)
        spb = None 

    return pb



class PatList(object): 

    def __init__(self, ): 
        self.patterns = OrderedDict () # name -> {}

        self.fieldOptions = ["SignalGroups", 
        "MacroDefs","Procedures","ScanStructures",
        "Start", "Stop","Termination", "Variables", 
        "If", "While", # TODO: Should these be 'here'
        ]
        

    def add_pattern(self, patname): 
        if patname in self.patterns: 
            raise RuntimeError("Pattern is already named:  %s"%(patname))
        self.patterns[patname] = {}
    
    def add_field(self, patname, key, value):
        if key not in self.fieldOptions: 
            raise ValueError("Option '%s' is not supported."%(key))
        self.patterns[patname][key] = value 
    
    def __getitem__(self, pattern): 
        if pattern in self.patterns: return self.patterns[pattern] 
        else: return None 
    
        

class ParallelPatList(PatList): 
    modes = ["SyncStart", "Independent", "LockStep"]

    def __init__(self,): 
        super(ParallelPatList, self).__init__()
        self.mode = 'Independent'
        self.fieldOptions = ["SignalGroups", 
        "MacroDefs","Procedures","ScanStructures",
        "Start", "Stop","Termination", "Variables", 
        "If", "While", # TODO: Should these be 'here'
        "Extend",
        ]

    def extend(self, pattern): 
        if pattern not in self.patterns: 
            raise RuntimeError("No pattern by the name is defined: %s"%(pattern))
        else: self.patterns[pattern]['Extend'] = True

class PatSet(PatList): 
    def __init__(self,): 
        super(PatSet, self).__init__()
        self.fieldOptions = ["SignalGroups", 
        "MacroDefs","Procedures","ScanStructures",
        "Start", "Stop","Termination", "Variables", 
        ]
        
