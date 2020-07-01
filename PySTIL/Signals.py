import re
import STILutils as sutils
import SymbolTable as STBL
 
class Signals(object): 
    def __init__(self, *args, **kwargs): 
        if "file" in kwargs: self._file = kwargs["file"] 
        else: self._file = None
        # TODO: Need a reference to the file is was found in. 
        # From the perspective of the a STIL translation, this would 
        # not be important, however, for reporting or tracing, we 
        # need to be clear which file this block is correspondants to. 

        if "mapping" in kwargs: self._mapping = kwargs["mapping"]
        else: raise ValueError("Must provide mapping value.") 

        # -------------------------------------------------------------
        # TODO: This entire block shoud be moved as a utility. 
        # TODO: If any shorthand entries covert for internal lookup table. 
        # 6.10: Signal and group name characteristics: 
        #   ex.) "a&b"[0..2] -> "a&b"[0], "a&b"[1], "a&b"[2]
        #   ex.) data[0] == data[00] != data00 // The brackets become part of the name 
        RE_brackets_with_dquotes = re.compile("^(?P<base>\"\w+\s*\")\[(?P<num1>\d+)\.+(?P<num2>\d+)\]\s*")
        RE_brackets_no_dquotes = re.compile("^(?P<base>\w+)\s*\[(?P<num1>\d+)\.+(?P<num2>\d+)\]\s*")
        self._shorthand = {}
        for signal in self._mapping:
            match = None 
            if RE_brackets_no_dquotes.search(signal):
                match = RE_brackets_no_dquotes.search(signal)
            elif RE_brackets_with_dquotes.search(signal): 
                match = RE_brackets_with_dquotes.search(signal)
            if match: 
                self._shorthand[signal] = []
                base = match.group("base") 
                num1 = int(match.group("num1"))
                num2 = int(match.group("num2"))
                if num2 > num1: 
                    for i in range(num1,num2+1,1):
                        self._shorthand[signal].append("%s[%d]"%(base,i))
                elif num1 > num2: 
                    for i in range(num1,num2+1,1):
                        self._shorthand[signal].append("%s[%d]"%(base,i))
                else: raise ValueError("Invalid syntax for '%s'"%(signal))

    def string(self, ): 
        retstr = []
        for signal in self._mapping: 
            retstr.append("%s: %s"%(signal, self._mapping[signal]))

        if self._shorthand: 
            retstr.append("Shorthands:")
            for signal in self._shorthand: 
                retstr.append("  - %s: %s"%(signal, self._shorthand[signal]))
        return "\n".join(retstr)

    def get_names(self, regex="", types=[]): 
        # Easy, simply return all names 
        if not regex and not types: 
            return list(self._mapping.keys())
        retList = []
        for signal in self._mapping:
            keep = True
            if regex: 
                if not re.search(regex, signal): 
                    keep = False 
            if types: 
                if self._mapping[signal]["type"] not in types: 
                    keep = False 
            if keep: 
                retList.append(signal)
        return retList


    @staticmethod
    def create_signals(string, file = "", debug=False): 
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
        signalsObject = Signals(mapping = signals)

        return signalsObject
       