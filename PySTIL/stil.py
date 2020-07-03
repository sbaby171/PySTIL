import sys, os, re, argparse
from collections import OrderedDict
import KeyLookUps as KLU
import SymbolTable as STBL
import STILutils as sutils
import Signals
import SignalGroups

# TODO: A key a question is to attached the APIs to the STIL object
#       or a set of APIs? 

class STIL(object): 

    def __init__(self, *args, **kwargs): 
        if "debug" in kwargs: self.debug = kwargs["debug"]
        else: self.debug = False
        
        # TODO: There are technical worries about always loading the STIL in a 
        # string and having to keep it as a string. The need for keeping it as 
        # a string is becasue we do a series of lookups for deeper analysis if 
        # requested. Moreover, this problem becomes exasterbated by the useage
        # of 'Includes' in the STIL file. 
        # 
        if "string" in kwargs: self._string = kwargs["string"]
        if not "file" in kwargs: self._filepath = None 
        else:     
            if not os.path.isfile(kwargs["file"]): 
                raise ValueError("Provided file doesn't exist: %s"%(kwargs['file']))
            self._filepath = kwargs['file']
            f = open(self._filepath,'r')
            self._string = f.read()
            f.close()
        
        if not self._string: raise ValueError("Must provide either 'string' OR 'file'.")

        if "all" in kwargs: self._all = kwargs["all"]
        else: self._all = False 

        if self._all:
            print("TODO: tokenize the entire stil nad build symboltable.")
            self._all = True
            self._tplp = None 
        else: 
            self._all = False
            self._tplp = OrderedDict()
        # ^^^ TODO: There is an honest question as to whether or not, we really 
        # need to have this distinction. In one way, this is helpful in that 
        # you can the need to create all the SymbolTables for each block in the 
        # toplevel-pointer dictionary. However, it is much easier to maintain
        # a single method of operation. Settings up this fork so early on 
        # maye cause many issues later on. 

        self.__parsed = False 
        self.__signals = None # NOTE: Will be an instance of 'Signals' class. 
        self.__signalGroups = [] # NOTE: List of SignalGroups objects.
        self.__userKeywords = [] # NOTE: List of string elements 



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
        for fileKey, tplp in self._tplp.items(): 
            if "SignalGroups" in tplp: 
                for entry in self._tplp[fileKey]["SignalGroups"]:   
                    tmp = self._string[entry['start']:entry['end'] + 1]
                    print("DEBUG: (%s): %s"%(func, entry))
                    self.__signalGroups.append(SignalGroups.SignalGroups.create_signalGroups(tmp, domainName=entry['name'], file=fileKey, debug = self.debug))
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
                    # TODO: 
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

