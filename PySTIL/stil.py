import sys, os, re, argparse
from collections import OrderedDict


import KeyLookUps as KLU
import SymbolTable as STBL
import STILutils as sutils


class Signal(object): 
    def __init__(self, *args, **kwargs): 
        if "file" in kwargs: self._file = kwargs["file"] 
        else: self._file = None
        # TODO: Need a reference to the file is was found in. 
        # From the perspective of the a STIL translation, this would 
        # not be important, however, for reporting or tracing, we 
        # need to be clear which file this block is correspondants to. 
        
        


    @staticmethod
    def create_signals(string, debug=False): 
        func = "Signals.create_signals"
        tokens = sutils.lex(string=string, debug=debug)
        sytbl  = STBL.SymbolTable(tokens=tokens, debug=debug) 

        if debug: 
            print("Tokens: ", tokens)
            print("SymbolTable: ", sytbl)
        # TODO: Create each object
        #  - Need to do this by eating the tokens (use symbolt table to help you)

        signals = {}
        typeList = ["In", "Out", "InOut", "Supply", "Psuedo"]

        token = {}
        signalName = ""
        signalType = ""
        i = 2; end = len(tokens) - 1; cbs = 0; 

        while i <= end: 
            token = tokens[i]

            if token['tag'] == "}": 
                cbs -= 1
                if cbs == 0: 
                    signalsName = ""; signalType = "";
                    i += 1; continue 

            if cbs == 1: 
                if token['tag'] == "ScanIn": 
                    if tokens[i+1]['tag'] == ';': 
                        signals[signalName] = {"type":signalType,
                                                   "ScanIn":True}
                        print("DEBUG: (%s): Added Signal: '%s' = %s"%(func, signalName, signals[signalName]))
                        i+=1; continue 
                    else: 
                        raise RuntimeError("Not ready to handle decimal scans")
                        # TODO: Else, use symbol table to grab the next token index 
                        # of the semicolon.
                if token['tag'] == "ScanOut": 
                    if tokens[i+1]['tag'] == ';': 
                        signals[signalName] = {"type":signalType,
                                                   "ScanOut":True}
                        print("DEBUG: (%s): Added Signal: '%s' = %s"%(func, signalName, signals[signalName]))
                        i+=1; continue 
                    else: 
                        raise RuntimeError("Not ready to handle decimal scans")
                        # TODO: Else, use symbol table to grab the next token index 
                        # of the semicolon.


            if cbs == 0: 
                if token['tag'] == "identifier": 
                    signalName = token['token']
                    if tokens[i+1]['tag'] not in typeList: 
                        print("Current: ", i, token)
                        print("Next   : ", i+1, tokens[i+1])
                        print("  - ", tokens[i+1]['tag'], type(tokens[i+1]['tag']))
                        raise ValueError("Invalid syntax of Signals")

                    else: 
                        signalType = tokens[i+1]['tag']
                        if tokens[i+2]['tag'] == ';': 
                            if signalName in signals: 
                                raise RuntimeError("Signal %s is already defined"%(signalName))
                                # ^^^ TODO: Is this valid? 
                            else: 
                                signals[signalName] = {"type":signalType}
                                print("DEBUG: (%s): Added Signal: '%s' = %s"%(func, signalName, signals[signalName]))

                                signalsName = ""; signalType = "";
                                i += 3; continue 
                        elif tokens[i+2]['tag'] == "{": 
                            cbs += 1 
                            i += 3; continue 
                        else: 
                            raise RuntimeError("Invalid syntax (i+2 != ; || {)")
                else: 
                    raise RuntimeError("Invalid syntax (cbs == 0 but not identifier)")
            i += 1

        # TODO: return signals? 
            

       


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
            print("TODO: TPLP.")
            self._all = False
            self._tplp = OrderedDict()
        # ^^^ TODO: There is an honest question as to whether or not, we really 
        # need to have this distinction. In one way, this is helpful in that 
        # you can the need to create all the SymbolTables for each block in the 
        # toplevel-pointer dictionary. However, it is much easier to maintain
        # a single method of operation. Settings up this fork so early on 
        # maye cause many issues later on . 

        self.__parsed = False 
        self.__signals = []



    def get_signalgroups(self, ): 
        if not self.__parsed: 
            raise RuntimeError("Make sure to parse STIL object before making queries.")
        retList = []
        for fileKey, value in self._tplp.items(): 
            #print(value)
            if "SignalGroups" in value["ObjectMap"]: 
                print("")
                for entry in value["ObjectMap"]["SignalGroups"]: 
                    retList.append(entry["name"])
        return retList 

    def get_signals(self, ): 
        # TODO: This should be returning a list of Signal objects
        # Because there can only be one Signals block per translation, 
        # it lends itself nicely to the implementation of a list of class
        # return.
        if self.__signals: return self.__signals 

        print("\nXXXX")
        # Create the Signal instances by referring to the tplp. 
        for fileKey, value in self._tplp.items(): 
            #if "Signals" in self._tplp[fileKey]: 
            for entry in self._tplp[fileKey]["Signals"]:   
                print(entry)
                tmp = self._string[entry['start']:entry['end'] + 1] # TODO: Not proper for includes.
                listOfSignals = Signal.create_signals(tmp, debug = self.debug)


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

            self._tplp[fileKey]["ObjectMap"] = objectMap
            # TODO: (MAYBE), Link the tplp and objectMap: self._tplp[fileKey]['ObjectMap'] = objectMap
            # Note, the problem with linking the object map to the tplp is that we have a bunch of 
            # redundant information noww. 
            # 
            # TODO: Becaue of this redundant information, it may be better to *replace* the 
            # the entry in tplp, for a given block, with the contents of the objct map. 
            #  ex.) self.__tplp[fileKey][<toplevelblock>] = objectMap[<toplevelblock>]
            for block in self._tplp[fileKey]: 
                if block in objectMap: 
                    print(block, self._tplp[fileKey][block], objectMap[block])
                else: 
                    print("Keeping old instance for: ", block)

            if self.debug:
                print("\nDEBUG: (%s): Obect Map on first pass: %s"%(func, fileKey))
                for key, value in objectMap.items(): 
                    print("DEBUG:   - %s: %s"%(key, value))
            
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
    parser.add_argument("--stil", help="STIL file path",)
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

    if args.debug: 
        print("DEBUG: Exiting PySTIL.stil")

