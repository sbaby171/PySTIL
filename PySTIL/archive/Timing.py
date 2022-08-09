import re
import STILutils as sutils
import SymbolTable as STBL
import KeyLookUps as KL



class TimingBlocks(sutils.Blocks): 
    def __init__(self): 
        super(TimingBlocks, self).__init__()
    def add(self, timing): 
        super(TimingBlocks, self).add(timing, Timing)

    def WaveformTables(self,regex=""): 
        """
        Return a list of WaveformTable objects found throughout STIL. 
        """
        retlist = []
        for timing in self.objects.values(): 
            retlist.extend(timing.WaveformTables(regex=regex))
        return retlist
    
# TODO: File needed? Probably for error handling and bookkeeping. 
class Timing(object): 
    def __init__(self, name, mapping, file = ""): 
        self.file = file 
        self.name = name
        self.mapping = mapping 
        #if "file" in kwargs: self.file = kwargs["file"] 
        #else: self.file = None
        #if "domain" in kwargs: self.domain = kwargs["domain"]
        #else: self.domain = ""
        #if "mapping" in kwargs: self._mapping = kwargs["mapping"]
        #else: raise ValueError("Must provide mapping value.")
        # TODO: Require a mapping is a bit specific. This is done becasue, to 
        # date, we are creating the Timing objects 'behind the scenes', meaning
        # the users do not see this. I suppose we can keep this for now.  
        #
        # NOTE: Remember a timing block can have many instances of WaveformTables. 
        # So we need to be sure how to maintain all this.
        # 
        self.waveformTables = {} # Instances of WaveformTable
        self.signalGroups   = ""
    def get_name(self,): return self.name
    def get_file(self,):   return self.file

    def WaveformTables(self, regex=""): 
        if not regex: 
            return self.waveformTables.values()
        retList = []
        for wvtbl in self.waveformTables:
            keep = True
            if regex: 
                if not re.search(regex, wvtbl): 
                    keep = False 
            if keep: 
                retList.append(self.waveformTables[wvtbl])
        return retList

    #def get_waveformtables(self, regex=""): 
    #    if not regex: 
    #        #return list(self.waveformTables.keys())
    #        return self.waveformTables.values()
    #    retList = []
    #    for wvtbl in self.waveformTables:
    #        keep = True
    #        if regex: 
    #            if not re.search(regex, wvtbl): 
    #                keep = False 
    #        if keep: 
    #            retList.append(self.waveformTables[wvtbl])
    #    return retList


    def add_waveformtable(self, wvtbl): 
        func = "%s.add_waveformtable"%(self.__class__.__name__)

        if not isinstance(wvtbl, WaveformTable): 
            raise ValueError("Must provide an intance of 'WaveformTable'.")
        
        if wvtbl.name in self.waveformTables: 
            raise RuntimeError("WaveformTable %s is already defined for timing block."%(wvtbl.name))
        else: self.waveformTables[wvtbl.name] = wvtbl

class WaveformTable(object): 
    def __init__(self, *args, **kwargs): 
        if "name" in kwargs: self.name = kwargs["name"] 
        else: self.name = ""
        if "period" in kwargs: self.period = kwargs["period"] 
        else: self.period = ""

        self.waveforms = None # Instance of Waveforms 
    
    def set_name(self, name): self.name = name
    def get_name(self, name): return self.name
    def set_period(self, period): self.period = period 

    def set_waveforms(self, waveforms): 
        if not isinstance(waveforms, Waveforms): 
            raise ValueError("'waveforms' must be of class 'Waveforms'.")
        self.waveforms = waveforms  

    def signals(self, ): 
        return self.waveforms.signals() 
    
    def contains(self, signal): 
        return self.waveforms.contains(signal)



class Waveform(object): 
    def __init__(self, *args, **kwargs): 
        if "signal" in kwargs: self.signal = kwargs["signal"] 
        else: self.signal = ""

        if "wfc" in kwargs: self.wfc = kwargs["wfc"] 
        else: self.wfc = []

        #self.wfc    = [] # The string will be pulled apart. 
        self.eqs    = [] # these will need to be separated just as wfc.  

    def __str__(self): 
        retstr = ["%s: %s {%s}"%(self.signal, self.wfc, self.eqs)]


        return "\n".join(retstr)
        

class Waveforms(object): 
    # Instance of a 'Waveforms' block as found within a WaveformTable. 
    def __init__(self, *args, **kwargs): 
        if "waveforms" in kwargs: self.waveforms = kwargs["waveforms"] 
        else: self.waveforms = []
        # ^^^ structure: 
        # ['CP'] -> {}
        #   ''   -> {'01':"'per/3' D/U;" }
        #   ''   -> {'01':"'per/3' D/U;" 
        #            'LH':"'equation';" }
        # TODO: While almost completely finished with the first version, i realized
        # i might want a separate class for Waveforms, however, to 
    def set_waveforms(self, waveforms): self.waveforms = waveforms 

    def __iter__(self,): 
        for signal in self.waveforms: 
            for waveform in self.waveforms[signal]: 
                yield waveform

    def signals(self,): 
        return list(self.waveforms.keys())

    def contains(self, signal): 
        if signal in self.waveforms: return True
        else: return False

        


    @staticmethod 
    def create_waveforms(tokens, symbolTable, waveformsIndex): 
        func = "Waveforms.create_waveforms"
        cbStart, cbEnd = symbolTable.get_next_set(waveformsIndex, "curly-brackets")

        waveforms = {}
        signalSEs = [] # List of tuples 

        i = cbStart + 1
        # NOTE: This loop only grab ths signal names and thier start and end cbs
        while i < cbEnd : 
            if (tokens[i]['tag'] == 'identifier'):
                signal = tokens[i]['token'] 
                #waveforms.append(Waveform(signal = signal))
                waveforms[signal] =  []  # [Waveform(signal=signal)]
                signalCbStart, signalCbEnd = symbolTable.get_next_curly_set(i)
                signalSEs.append((signal, signalCbStart,signalCbEnd))
                i = signalCbEnd + 1
                continue 
            else: 
                raise RuntimeError("Recieved on 'identifer' at %d, '%s'"%(i, tokens[i]))

        RE_WFC_WFCLIST = re.compile("[a-zA-Z\d]+")
        for signal, start, end in signalSEs: 
            i = start + 1
            wfc = False 
            definition = False 
            while i <= end: 
                if not wfc: 
                    match = RE_WFC_WFCLIST.search(tokens[i]['token'])
                    if match: 
                        wfc = match.group()
                        waveforms[signal].append(Waveform(signal=signal, wfc=wfc))
                        i += 1; continue 
                if not definition: 
                    if tokens[i]['tag'] == '{': 
                        cbGroups = symbolTable.instances_in_range(i, end, '{', inclusive=True)
                        if len(cbGroups) == 1: 
                            waveforms[signal][-1].eqs = symbolTable.string_token_range(tokens,i+1,cbGroups[-1][-1]-1)
                        elif len(cbGroups) == 0: 
                            raise RuntimeError("Recieved no curly brackets groups. Expecting one.")
                        elif len(cbGroups) >= 1: 
                            waveforms[signal][-1].eqs = symbolTable.string_token_range(tokens,i+1,cbGroups[0][-1]-1)

                            i = cbGroups[0][-1]
                            wfc = False
                            continue
                    i += 1; continue; 
        waveforms = Waveforms(waveforms=waveforms)
        return waveforms

# NOTE: For Period we will simply store the Period, and report 
# back. We may not need to evaluate... even if spec variables are 
# used. 
# NOTE: A note on the hierarchy, 
# Timing
# |----> WaveformTable
#        |----> Waveforms (block)
#               |----> waveforms (singles)
#                      |----> WFC or WFC_LIST
#
def create_timing(string, name = "", file = "", debug=False):
    func = "Timing.create_timing"
    tokens = sutils.lex(string=string, debug=debug)
    sytbl  = STBL.SymbolTable(tokens=tokens, debug=debug) 
    timing = Timing(name=name,file=file, mapping={})
    #if debug: 
    #    print("DEBUG: (%s): Tokens: %s "% (func, tokens))
    #    print("DEBUG: (%s): SymbolTable: %s"%(func, sytbl))
    wvfmtbls = sytbl["WaveformTable"]
    #print(wvfmtbls)
    #cbSet = sytbl.get_next_set(wvfmtbls[0], "curly-brackets")
    #print(cbSet)
    for wvtblIndex in wvfmtbls: 
        cbStart, cbEnd = sytbl.get_next_set(wvtblIndex, "curly-brackets")
        # Extract WaveformTable name: 
        # --------------------------: 
        if ((cbStart - wvtblIndex) != 2): 
            raise RuntimeError("The difference between WaveformTable and starting bracket should be 2.")
        if tokens[wvtblIndex + 1]['tag'] != 'identifier': 
            raise RuntimeError("WaveformTable names should be of type 'identifier'.")
        waveformTableName = tokens[wvtblIndex + 1]['token']
        if debug: print("DEBUG: (%s): Found WaveformTable name: %s"%(func, waveformTableName))
        # Extract WaveformTable Period: 
        # ----------------------------: 
        # The check here is that we need only ONE period defintion within the 
        # cbStart and cbEnd range. 
        # Moreover, because a Timing block can have multiple WaveformTable 
        # instances, more than one period instance cand be returned by the 
        # sytbl['Period'] query.
        periodIndex = sytbl.instances_in_range(cbStart, cbEnd, 'Period')
        if (len(periodIndex) > 1): 
            raise RuntimeError("There should only be one instance of 'Period' "\
                "for a given WaveformTable. See WaveformTable '%s' definition."\
                %(waveformTableName))
        closingPeriodIndex = sytbl.get_next_instance(periodIndex[0],';')
        #print("Closing Period index: ", closingPeriodIndex)

        #for k, token in enumerate(tokens): 
        #    print(k , token) 

        period = sytbl.string_token_range(tokens, periodIndex[0]+1, closingPeriodIndex-1)

        #if (tokens[periodIndex[0] + 4]['tag'] != ';'):
        #    raise RuntimeError("Expecting a semicolon to terminate Period statement."\
        #        "Instead found: tokens[%d]['tag'] = %s"%(periodIndex[0]+2, tokens[periodIndex[0] + 2]['tag']))

        waveformTablePeriod = period
        # TODO: InheritWaveformTable
        
        # TODO: At this point, we need to go now offload the waveforms block
        # onto another method. 
        # NOTE: "Only one Waveforms block shall appear in a WaveformTable block".
        waveformsIndex = sytbl.instances_in_range(cbStart, cbEnd, 'Waveforms')
        if (len(waveformsIndex) > 1): 
            raise RuntimeError("There should only be one 'Waveforms' block "\
                "for a given WaveformTable. See WaveformTable '%s' definition."\
                %(waveformTableName)) 
        # NOTE: I dont need to stringify the waveforms block! I simply 
        # need to give the Waveforms block the proper pointers and 
        # the tokens list!
        waveformtable = WaveformTable(name = waveformTableName,
                                      period = waveformTablePeriod)

        waveformtable.set_waveforms(Waveforms.create_waveforms(tokens = tokens, 
        symbolTable= sytbl, waveformsIndex = waveformsIndex[0])) 
        timing.add_waveformtable(waveformtable)
    return timing  



    # TODO: This naming 'create_*' is true in the sense that it creates 
    # waveforms, however, it is missing the important point that it is 
    # creating them from parsing strings. Thus, we should reconsider how 
    # we name these functions.
    #def create_waveforms() 

