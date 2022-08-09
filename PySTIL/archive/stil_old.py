import sys, os, re, argparse, gzip
from collections import OrderedDict
import KeyLookUps as KLU
import SymbolTable as STBL
import STILutils as sutils
import Signals
import SignalGroups
import Timing
import Spec
import PatternBurst 

# TODO: A key a question is to attached the APIs to the STIL object
#       or a set of APIs? 

GLOBAL = ' '

class STIL(object): 

    def __init__(self, *args, readpath = "", writepath = "", **kwargs): 
        if "debug" in kwargs: self.debug = kwargs["debug"]
        else: self.debug = False

        self._readpath  = readpath
        self._writepath = writepath 
        self._read = False 
        self._tplp = OrderedDict() 

        # TODO: There are technical worries about always loading the STIL in a 
        # string and having to keep it as a string. The need for keeping it as 
        # a string is becasue we do a series of lookups for deeper analysis if 
        # requested. Moreover, this problem becomes exasterbated by the useage
        # of 'Includes' in the STIL file. 
        # 


        #if "all" in kwargs: self._all = kwargs["all"]
        #else: self._all = False 
        #if self._all:
        #    print("TODO: tokenize the entire stil nad build symboltable.")
        #    self._all = True
        #    self._tplp = None 
        #else: 
        #    self._all = False
        #    self._tplp = OrderedDict()
        # ^^^ TODO: There is an honest question as to whether or not, we really 
        # need to have this distinction. In one way, this is helpful in that 
        # you can the need to create all the SymbolTables for each block in the 
        # toplevel-pointer dictionary. However, it is much easier to maintain
        # a single method of operation. Settings up this fork so early on 
        # maye cause many issues later on. 

        self.__parsed = False 
        self.signal = None 
        # NOTE: Because there can only be a single Signal block per stil 
        # translaion


        self.__signalGroups = [] # TODO: Remove all remebrants


        self.__signals = None # TODO: Remove. Relic of the past 
        self._SignalsBlock = None # NOTE: Will be an instance of 'Signals' class. 
        self._SignalGroupsBlocks = None
        self._TimingBlocks = None 
        self._SpecBlocks = None 
        self._SelectorBlocks = None 

        self._PatternBurstBlocks = None
    
        self.__userKeywords = [] # NOTE: List of string elements 

    def write(self, writepath=""): 
        """ 
        This method will convert its contents to a valid STIL file. 
        """
        func = "%s.write"%(self.__class__.__name__)

        # Sanity Checks: 
        # --------------
        if self._writepath and writepath: 
            raise RuntimeError("(%s): Two writepaths have been provided: %s, %s"%(func, self._writepath, writepath)) 
        if writepath: 
            # TODO: Check path and create what needs to be created. 
            self._writepath = writepath 
        if not self._writepath or not writepath: 
            raise RuntimeError("(%s): No writepath has been provided yet."%(func)) 

        return 


    def read(self, readpath=""): 
        """
        This funciton is to read the referenced STIL file and perform
        intial processing. This method does not return anything. All of 
        its effects are internal to the STIL object. 

        If readpath is provided while the STIL object has already had a 
        readpath set, the method will throw an error. Otehrwise, the path
        will be checked and it will be set to the readpath of the STIL 
        object. 
        """ 
        func = "%s.read"%(self.__class__.__name__)

        # Sanity Checks: 
        # --------------
        if self._readpath and readpath: 
            raise RuntimeError("(%s): Two readpaths have been provided: %s, %s"%(func, self._readpath, readpath)) 
        if readpath: 
            if not os.path.isfile(readpath): 
                raise RuntimeError("(%s): Readpath does not exist: %s)"%(readpath))
            self._readpath = readpath 
        if not self._readpath and not readpath: 
            raise RuntimeError("(%s): No readpath has been provided yet."%(func)) 
        if self._read: return 

        # TODO: Before processing we may have to move to /tmp
        #   - how to check if windows or linux
        #   - on linux, we would move to /tmp, what would be the eqv on windows? 
        #   - how to check if file is gz? 

        # Annex C: GNU GZIP Reference: 
        # "STIL files may be compressed using the GNU GZIP (deflate) program. Compressing
        # files addresses the concerns with transferring and storing huge ammounts data 
        # associated with the design and testing of complex digital VLSI circuits."


        self._fileKeyToPathDict = {}
        self._moveProcessingTo = "" 
        # ^^^ TODO: Move these 

        fileKey = os.path.basename(self._readpath)
        if self._moveProcessingTo: 
            fileKeyPath = os.join(self._moveProcessingTo, fileKey)
            # TODO: Will need to remove '.gz' if present and recompress file at dest. 
            print("TODO: Moving Processing is set but implementation is not done.")
            sys.exit(1)
        else: self._fileKeyToPathDict[fileKey] = self._readpath 

        if fileKey.endswith(".gz"): gunzip = True 
        else: gunzip = False 
        #print("DEBUG: (%s) Setting gunzip flag true. Found '.gz' at suffix."%(func))
        if not gunzip: 
            f = open(self._fileKeyToPathDict[fileKey],'r')
            string = f.read()
            f.close()
        else: 
            f = gzip.open(self._fileKeyToPathDict[fileKey],'rt')
            string=f.read()
            f.close()
     
        # (1) Execute first layer of tpl tagger
        self._tplp = sutils.tpl_tagger( tplp     = self._tplp, 
                                        fileKey  = fileKey, 
                                        string   = string, 
                                        debug    = self.debug)
        if self.debug: 
            print("\nDEBUG: (%s): First layer pass 'toplevel-pointer': %s"%(func, fileKey))
            for key, value in self._tplp[fileKey].items(): 
                print("DEBUG:   - %s : %s"%(key,value))                

        # (2) Execute sanity check and priliminary object builder. 
        objectMap = sutils.tplp_check_and_object_builder(string  = string, 
                                                         tplp    = self._tplp,
                                                         fileKey = fileKey,
                                                         debug   = self.debug,) 

        # Relpace the blocks with those in the
        for block in self._tplp[fileKey]: 
            if block in objectMap: 
                self._tplp[fileKey][block] = objectMap[block]
            else: pass  # Keep original grouping. 

        if self.debug:
            print("\nDEBUG: (%s): tplp after first layer sanity check: %s"%(func, fileKey))
            for block in self._tplp[fileKey]: 
                print("DEBUG:  - %s:  %s"%(block, self._tplp[fileKey][block]))
            
        # (3): If Includes present, we must recusively checks these, 
        includeProcessing = True
        if includeProcessing: 
            if "Include" in objectMap: 
                print("DEBUG: (%s): TODO: Working on the includes..."%(func))

                includesList = objectMap["Include"]
                i = 0

                while i < len(includesList): 
                    include = includesList[i]['file']
                    print("DEBUG: (%s): TODO: Checking the following include file: %s"%(func, include))

                    includeBaseName = os.path.basename(include)
                    includePath     = os.path.dirname(include)
                    if not includePath: 
                        includePath = os.path.dirname(self._readpath)
                    print("DEBUG: (%s): Include path: %s"%(func, includePath))
                    print("DEBUG: (%s): Include basename: %s"%(func,includeBaseName))
                    if self._moveProcessingTo: 
                        fileKeyPath = os.join(self._moveProcessingTo, fileKey)
                        # TODO: Will need to remove '.gz' if present and recompress file at dest. 
                        print("TODO: Moving Processing is set but implementation is not done.")
                        sys.exit(1)
                    else: self._fileKeyToPathDict[includeBaseName] = os.path.join(includePath,includeBaseName)

                    if includeBaseName.endswith(".gz"): gunzip = True 
                    else: gunzip = False 
                    #print("DEBUG: (%s) Setting gunzip flag true. Found '.gz' at suffix."%(func))
                    if not gunzip: 
                        f = open(self._fileKeyToPathDict[includeBaseName],'r')
                        string = f.read()
                        f.close()
                    else: 
                        f = gzip.open(self._fileKeyToPathDict[includeBaseName],'rt')
                        string=f.read()
                        f.close()

                    self._tplp = sutils.tpl_tagger( tplp    = self._tplp, 
                                                    fileKey = includeBaseName, 
                                                    string = string, 
                                                    debug   = self.debug) 

                    objectMap  = sutils.tplp_check_and_object_builder( tplp = self._tplp,
                                                                       fileKey = includeBaseName,
                                                                       string = string,
                                                                       debug   = self.debug,) 
                    print("Include objectMap: %s"%(objectMap))
                 
                    # Relpace the blocks with those in the
                    for block in self._tplp[includeBaseName]: 
                        if block in objectMap: 
                            self._tplp[includeBaseName][block] = objectMap[block]
                        else: pass  # Keep original grouping.
                    self.print_tplp()


                # sanity check: 
                # TODO: Check all domain names across necessary fields - 
                # remember the tpl checker method is checking for domain on within each 
                # STIL os here we need to be checking across the entire Stil.
                # 
                # ^^^ TODO: Need a way to examine store the string-representation for each 
                    tmpObjMap = {}
                    # include.
                    if 'Include' in tmpObjMap: 
                        includesList += tmpObjMap['Include']
                        self._tplp[include] = tmpObjMap
                    
                    i += 1

        self._read = True
        return 
        

    def print_tplp(self,): 
        for filekey in self._tplp: 
            print("FILE: %s:"%(filekey))
            for block in self._tplp[filekey]: 
                print(" - %s: "%(block))
                for entry in self._tplp[filekey][block]: 
                    print("    * %s"%(entry)) 
        return

    # ------------------------------------------------------------------------: 
    # TODO: Note thaat we have not created a self._Includes field. In general, 
    # using the 'self._<field>' should be worry some if 'writing' is allowed. 
    # This is because a diconnect can occur: read -> set field -> user adds 
    # block -> read again ... there will be a disconnect here .
    def Includes(self, ): 
        """ 
        Return list of Include references. 
        """
        retdict = OrderedDict()
        for filekey in self._tplp: 
            if "Include" in self._tplp[filekey]: 
                retdict[filekey] = self._tplp[filekey]["Include"]
        return retdict 
    
    def has_Includes(self,):
        """Return boolean based on if STIL contains 'Includes'."""
        for filekey in self._tplp: 
            if "Include" in self._tplp[filekey]: return True 
            else: pass 
        return False 
                


    # ------------------------------------------------------------------------: 


    # NOTE: "The standard doesn't explicitly allow/disallow quoted user 
    # keywords. However, we do NOT ALLOW that since user keywords are 
    # intended to 'extend' standard STIL language keywords, in other words
    # create a user version of STIL. STIL STIL doesnt allow auoted keywords 
    # we assumed its reasonable to require UserKeywords to be used without
    # quotes as well, to make user version of STIL language look similiar 
    # to the core STIL."

 
    def Signals(self,): 
        if not self._read: 
            raise RuntimeError("Make sure to parse STIL object before making queries.")
        if self._SignalsBlock: return self._SignalsBlock 

        # Create the Signal instances by referring to the tplp. 
        for fileKey, value in self._tplp.items(): 
            #if "Signals" in self._tplp[fileKey]: 
            for entry in self._tplp[fileKey]["Signals"]:   
                # -------------------------------------------------------: 
                string = sutils.file_as_string(self._fileKeyToPathDict[fileKey])
                # -------------------------------------------------------
                tmp = string[entry['start']:entry['end'] + 1] # TODO: Not proper for includes.
                self._SignalsBlock = Signals.create_signals(tmp, file = fileKey, debug = self.debug)
                # TODO: Should fileKey be passed in at 'create_signals'? 
                return self._SignalsBlock 
        # TODO: Becasue we return after the first instance, during the 
        # sanity checking at parse, we must ensure that all other Signal
        # entries are deleted. 


    def Timings(self,): 
        func = "%s.timing"%(self.__class__.__name__)
        if not self._read: 
            raise RuntimeError("Make sure to parse STIL object before making queries.")
        if self._TimingBlocks: return self._TimingBlocks
        self._TimingBlocks = Timing.TimingBlocks()
        for fileKey, tplp in self._tplp.items(): 
            if "Timing" in tplp: 
                for entry in self._tplp[fileKey]["Timing"]:   
                    # -------------------------------------------------------: 
                    string = sutils.file_as_string(self._fileKeyToPathDict[fileKey])
                    # -------------------------------------------------------:
                    tmp = string[entry['start']:entry['end'] + 1]
                    if self.debug: print("DEBUG: (%s): %s"%(func, entry))
                    timing = Timing.create_timing(tmp, name=entry['name'], file=fileKey, debug = self.debug)
                    self._TimingBlocks.add(timing)
        return self._TimingBlocks

    def PatternBursts(self,): 
        func = "%s.PatternBursts"%(self.__class__.__name__)
        if not self._read: 
            raise RuntimeError("Make sure to `read` the STIL before making queries.")
        if self._PatternBurstBlocks: return self._PatternBurstBlocks
        self._PatternBurstBlocks = PatternBurst.PatternBurstBlocks()

        for fileKey, tplp in self._tplp.items(): 
            if "PatternBurst" in tplp: 
                for entry in self._tplp[fileKey]["PatternBurst"]:   
                    # -------------------------------------------------------: 
                    string = sutils.file_as_string(self._fileKeyToPathDict[fileKey])
                    # -------------------------------------------------------: 
                    tmp = string[entry['start']:entry['end'] + 1]
                    if self.debug: print("DEBUG: (%s): %s"%(func, entry))
                    pb = PatternBurst.create_PatternBurst(tmp, name=entry['name'], file=fileKey, debug = self.debug)
                    self._PatternBurstBlocks.add(pb)
        return self._PatternBurstBlocks

    def Specs(self,): 
        func = "%s.specs"%(self.__class__.__name__)
        if not self._read: 
            raise RuntimeError("Make sure to parse STIL object before making queries.")
        if self._SpecBlocks: return self._SpecBlocks
        self._SpecBlocks = Spec.SpecBlocks()

        for fileKey, tplp in self._tplp.items(): 
            if "Spec" in tplp: 
                for entry in self._tplp[fileKey]["Spec"]:   
                    print("DEBUG: (%s) Processing %s for Specs blocks."%(func,fileKey))
                    # -------------------------------------------------------: 
                    string = sutils.file_as_string(self._fileKeyToPathDict[fileKey])
                    # -------------------------------------------------------: 
                    tmp = string[entry['start']:entry['end'] + 1]
                    if self.debug: print("DEBUG: (%s): %s"%(func, entry))
                    spec = Spec.create_spec(tmp, name=entry['name'], file=fileKey, debug = self.debug)
                    self._SpecBlocks.add(spec)
        return self._SpecBlocks

    def SignalGroups(self,): 
        func = "%s.SignalGroups"%(self.__class__.__name__)
        if not self._read: 
            raise RuntimeError("Make sure to parse STIL object before making queries.")
        if self._SignalGroupsBlocks: return self._SignalGroupsBlocks
        self._SignalGroupsBlocks = SignalGroups.SignalGroupsBlocks()

        for fileKey, tplp in self._tplp.items(): 
            if "SignalGroups" in tplp: 
                for entry in self._tplp[fileKey]["SignalGroups"]:   
                    if self.debug: print("DEBUG: (%s) Processing %s for SignalGroups blocks."%(func,fileKey))
                    # -------------------------------------------------------: 
                    string = sutils.file_as_string(self._fileKeyToPathDict[fileKey])
                    # -------------------------------------------------------: 
                    tmp = string[entry['start']:entry['end'] + 1]
                    if self.debug: print("DEBUG: (%s): %s"%(func, entry))
                    siggrp = SignalGroups.create_signalGroups(tmp, name=entry['name'], file=fileKey, debug = self.debug)
                    self._SignalGroupsBlocks.add(siggrp)
        return self._SignalGroupsBlocks

    # TODO: Remember, you could always create a generic API and 
    # embed the branched logic wihtin that. Example, "get_blocks('Spec')"
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

 
        

    def get_userkeyword(self, key): 
        if not self.__parsed: 
            raise RuntimeError("Make sure to parse STIL object before making queries.")

        if self.__userKeywords: return self.__userKeywords
        
        retlist = []
        for fileKey in self._tplp: 
            if key in self._tplp[fileKey]: 
                for instance in self._tplp[fileKey][key]: 
                    start = instance['start']
                    end = instance['end']
                    tmp = self._string[start:end]
                    retlist.append(tmp)
        self.__userKeywords = retlist 
        return self.__userKeywords

    # TODO: Which API is better? I am leaning towards no 'get_'
    def signalGroups(self,): 
        func = "%s.signalGroups"%(self.__class__.__name__)
        if not self.__parsed: 
            raise RuntimeError("Make sure to parse STIL object before making queries.")
        
        if self._SignalGroupsBlocks: return self._SignalGroupsBlocks

        self._SignalGroupsBlocks = SignalGroups.SignalGroupsBlocks()
        for fileKey, tplp in self._tplp.items(): 
            if "SignalGroups" in tplp: 
                for entry in self._tplp[fileKey]["SignalGroups"]:   
                    tmp = self._string[entry['start']:entry['end'] + 1]
                    if self.debug: print("DEBUG: (%s): %s"%(func, entry))
                    siggrp = SignalGroups.SignalGroups.create_signalGroups(tmp, domainName=entry['name'], file=fileKey, debug = self.debug)
                    self._SignalGroupsBlocks.add(siggrp)
        return self._SignalGroupsBlocks
        


    def get_signalgroups(self, domain="", ): 
        """
        NOTE: domain is not a regex. It is a direct match.
        """
        func = "%s.get_signalgroups"%(self.__class__.__name__)
        if not self.__parsed: 
            raise RuntimeError("Make sure to parse STIL object before making queries.")

        if self.__signalGroups: 
            if domain: 
                for entity in self.__signalGroups: 
                    if domain == entity.get_domain():
                        return entity
                return None 
            if not domain: 
                return self.__signalGroups

        # Create the Signal instances by referring to the tplp. 
        self._SignalGroupsBlocks = SignalGroups.SignalGroupsBlocks()

        for fileKey, tplp in self._tplp.items(): 
            if "SignalGroups" in tplp: 
                for entry in self._tplp[fileKey]["SignalGroups"]:   
                    tmp = self._string[entry['start']:entry['end'] + 1]
                    if self.debug: print("DEBUG: (%s): %s"%(func, entry))

                        
                    siggrp = SignalGroups.SignalGroups.create_signalGroups(tmp, domainName=entry['name'], file=fileKey, debug = self.debug)
                    self.__signalGroups.append(siggrp)
                    # NOTE: I think this is what we are changin here, rather than keeping a list of these objects, 
                    # we will be storing instances in the <type>Blocks. 
                    # Example) SignalGroupsBlocks, TimingBlocks, DcLevelsBlock.
                    self._SignalGroupsBlocks.add(siggrp)


                    #self.__signalGroups[-1].file = fileKey 
                    # TODO: Should fileKey be passed in at 'create_signals'? 

        if domain: 
            for entity in self.__signalGroups: 
                if domain == entity.get_domain():
                    return entity
            return None 

        if not domain: 
            return self.__signalGroups

        return self.__signalGroups 


    # TODO: Consider which API makes more sense.
    def signals(self, ): 
        return self.get_signals()

    def get_signals(self, ): 
        """ 
        This method will return the 'Signals' class object. 
        Because, there is only one Signals blocks per translation according to the
        standard, we return a single object.
        """
        if not self.__parsed: 
            raise RuntimeError("Make sure to parse STIL object before making queries.")

        if self.__signals: return self.__signals 

        # Create the Signal instances by referring to the tplp. 
        for fileKey, value in self._tplp.items(): 
            #if "Signals" in self._tplp[fileKey]: 
            for entry in self._tplp[fileKey]["Signals"]:   
                tmp = self._string[entry['start']:entry['end'] + 1] # TODO: Not proper for includes.
                self.__signals = Signals.Signals.create_signals(tmp, file = fileKey, debug = self.debug)
                # TODO: Should fileKey be passed in at 'create_signals'? 
                return self.__signals 
        # TODO: Becasue we return after the first instance, during the 
        # sanity checking at parse, we must ensure that all other Signal
        # entries are deleted. 
    

 


    def selectors(self,): 
        func = "%s.selectors"%(self.__class__.__name__)
        if not self.__parsed: 
            raise RuntimeError("Make sure to parse STIL object before making queries.")
        if self._SelectorBlocks: return self._SelectorBlocks
        self._SelectorBlocks = Spec.SelectorBlocks()

        for fileKey, tplp in self._tplp.items(): 
            if "Selector" in tplp: 
                for entry in self._tplp[fileKey]["Selector"]:   
                    tmp = self._string[entry['start']:entry['end'] + 1]
                    if self.debug: print("DEBUG: (%s): %s"%(func, entry))
                    spec = Spec.create_selector(tmp, name=entry['name'], file=fileKey, debug = self.debug)
                    self._SelectorBlocks.add(spec)
        return self._SelectorBlocks


    def parse(self, ): 
        func = "STIL.parse"

        if self._tplp is not None: 
            if not self._filepath : fileKey = 'string'
            else:                   fileKey = os.path.basename(self._filepath)
            # (1) Execute first layer of tpl tagger
            self._tplp = sutils.tpl_tagger( self._tplp, 
                                            fileKey = fileKey, 
                                            string = self._string, 
                                            debug = self.debug)
            if self.debug: 
                print("\nDEBUG: (%s): First layer pass 'toplevel-pointer': %s"%(func, fileKey))
                for key, value in self._tplp[fileKey].items(): 
                    print("DEBUG:   - %s : %s"%(key,value))                
            # (2) Execute sanity check and priliminary object builder. 
            objectMap = sutils.tplp_check_and_object_builder(string  = self._string, 
                                                             tplp    = self._tplp,
                                                             fileKey = fileKey,
                                                             debug   = self.debug,) 

            # Relpace the blocks with those in the
            for block in self._tplp[fileKey]: 
                if block in objectMap: 
                    self._tplp[fileKey][block] = objectMap[block]
                else: pass  # Keep original grouping. 

            if self.debug:
                print("\nDEBUG: (%s): tplp after first layer sanity check: %s"%(func, fileKey))
                for block in self._tplp[fileKey]: 
                    print("DEBUG:  - %s:  %s"%(block, self._tplp[fileKey][block]))
                #for key, value in objectMap.items(): 
                #    print("DEBUG:   - %s: %s"%(key, value))
            
            # (3): If Includes present, we must recusively checks these, 
            if "Include" in objectMap: 
                print("DEBUG: (%s): TODO: Working on the includes..."%(func))

                includesList = objectMap["Include"]
                i = 0

                while i < len(includesList): 
                    include = includesList[i]['file']
                    print("DEBUG: (%s): TODO: Checking the following include file: %s"%(func, include))
                    #self._tplp = sutils.tpl_tagger(self._tplp, fileKey=include, file = include, debug = self.debug) 
                    #tmpObjMap  = sutils.tplp_check_and_object_builder( tplp    = self._tplp,
                    #                                           fileKey = include,
                    #                                            debug   = self.debug,) 
                    # 
                    # sanity check: 
                    # TODO: Check all domain names across necessary fields - 
                    # remember the tpl checker method is checking for domain on within each 
                    # STIL os here we need to be checking across the entire Stil.
                    # 
                    # ^^^ TODO: Need a way to examine store the string-representation for each 
                    tmpObjMap = {}
                    # include.
                    if 'Include' in tmpObjMap: 
                        includesList += tmpObjMap['Include']
                        self._tplp[include] = tmpObjMap
                    
                    i += 1
            
        # TODO: Compare ALL Domain names for compatiability. 
        #   ex.) All signalGroups names,
        #   ex.) All Pattern and PatternBurst names. 

        self.__parsed = True


        # TODO: Should this method be a manager that splits in the variosu methods to 
        # for a cleaner handliing? 
        if self._all: 
            print("\nNOTE: We are not handling 'all' at them moment")
            sys.exit(1)
            self._all_tokens  = sutils.lex(string = self._string, debug = self.debug)
            self._all_sytbl   = STBL.SymbolTable(tokens=self._all_tokens, debug = self.debug)


            if self.debug: 
                print(self._all_sytbl)

            # TODO: Sanity check
            # TODO: If any includes - make the list 
            if self._all_sytbl["Include"]: 
                print("Include present")
            else: 
                print("Include not present")



        


def greetings(): 
    retstr = "Greetings from PySTIL.stil" + "\n"\
        + KLU.greetings() + "\n" + STBL.greetings()
    return retstr

def _handle_cmd_args(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Increase console logging", action="store_true")
    parser.add_argument("--interactive", help="Interactive mode", action="store_true")
    parser.add_argument("--all", help="Tokenize entire STIL", action="store_true")
    parser.add_argument("stil", help="STIL file path",)
    args = parser.parse_args()

   
    if not os.path.isfile(args.stil): 
        raise ValueError("Invalid STIL file.")

    return args

if __name__ == "__main__":
    args = _handle_cmd_args()
    so = STIL(file = args.stil, all = args.all, debug = args.debug)
    so.parse()
    if args.interactive: 
        print("TODO: Need to implement interactive mode....")
        print(so._tplp)



    if args.debug: 
        print("DEBUG: Exiting PySTIL.stil")

