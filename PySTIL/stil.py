import sys, os, re


import utils
import SignalsBlock as SB

SEMICOLON = "semicolon"
STARTCURLY = "startcurly"
ENDCURLY = "endcurly"
ENTITY = "entity"
whitespace_character = [" ", "\t", "\n"]


class Header(object): 
    def __init__(self, *args, **kwargs):
        self.title = ""
        self.date = ""
        self.source = ""
        self.history = []

    def get_title(self): 
        return self.title

    def get_date(self): 
        return self.date
    
    def get_source(self):
        return self.source

    def get_history(self): 
        for ann in self.history: 
            yield ann

    def __str__(self):
        ret_str = ["Header { \n"]
        if self.title: 
            ret_str.append("  Title \"%s\";\n"%(self.title))
        if self.date: 
            ret_str.append("  Date \"%s\";\n"%(self.date))
        if self.source: 
            ret_str.append("  Source  \"%s\";\n"%(self.source))
        if self.history:
            ret_str.append("  History { \n")
            for ann in self.history: 
                ret_str.append("    {* " + ann +"*}\n")
            ret_str.append("  }\n")
        ret_str.append("}\n")
        return "".join(ret_str)


        

class STIL(object): 

    def __init__(self,*args,**kwargs): 
        if "debug" in kwargs: self.debug = kwargs["debug"]
        else: self.debug = None 

        if "sfp" in kwargs: self.sfp = kwargs["sfp"]
        else: self.sfp = None 
            
        self.stil_version = None 
        self.header = None
        self.signals = None


        # This data structure is important for the parsing methods. 
        self.TOPLEVEL = {
            "STIL" : {
                "ending": ";",
                "processor" : self.__stil_processor, 
            },
            "Header" : {
                "ending": "}",
                "processor" : self.__header_processor, 
            },
            "Signals" : {
                "ending": "}",
                "processor" : self.__signals_processor, 
            },
            "SignalGroups": {
                "ending": "}",
                "processor" : self.__signalgroups_processor, 
            } 
        }
        self.__states = {
            "FREE" : True,
        }

        self.__map = {}
        # ^^ this map will be filled with

    def __stil_processor(self, value): 
        if self.debug: print("STIL STATEMENT: recieved: ", value)
        RE_STIL_VERSION = re.compile("STIL\s+(?P<version>[\d\.]+)\s*;")
        match = RE_STIL_VERSION.search(value)
        if match: 
            self.stil_version = match.group("version")
            if self.debug: print("SITL VERSION: %s"%(self.stil_version))

    def __header_processor(self, value): 
        if self.debug: print("Header STATEMENT: recieved: ", value)
        self.header = Header()

        _interal_state = []
        title_section = False
        date_section = False
        source_section = False

        string_literal = False
        lastchar  = ''
        identifier = []
        firstcurly = 0
        for char in value: 

            if char == "{" and not firstcurly: 
                firstcurly = 1
                continue 
            if not firstcurly: continue 
            # ----------------------------------------------------- S: String-literal
            if  title_section or date_section or source_section: 
                if string_literal: 
                    if char == "\"" and lastchar != "\\": # Closing string-literal
                        _str = "".join(identifier); identifier = []
                        if title_section: 
                            self.header.title = _str
                            title_section = False
                        elif date_section: 
                            self.header.date = _str
                            date_section = False
                        elif source_section: 
                            self.header.source = _str
                            source_section = False
                        else: 
                            raise RuntimeError("no expecting a string literal ")
                        string_literal = False
                        continue 
                    else: 
                        identifier.append(char)
                        continue 
                # ----------------------------------------------------- Freelance: String-literal start. 
                if char == "\"":  # TODO: could ad 'and state["notdone"]'
                    string_literal = True
                    continue
            lastchar = char   
            if char not in whitespace_character: 
                if char != ";":
                    identifier.append(char)
            else: 
                if len(identifier) == 0: continue 
                thing = "".join(identifier); identifier = []
                if thing == "Title": 
                    title_section = True
                if thing == "Date": 
                    date_section = True
                if thing == "Source": 
                    source_section = True
        """
        #RE_TITLE = re.compile("Title\s+\"(?P<title>.*)\"\s*;")
        RE_TITLE = re.compile("Title\s+\"(?P<title>.)\"\s*;")
        match = RE_TITLE.search(value)
        if match: 
            self.header.title = match.group("title")
            if self.debug: print("HEADER-TITLE: %s"%(self.header.title))
    
        RE_DATE= re.compile("Date\s+\"(?P<date>.*)\"\s*;")
        match = RE_DATE.search(value)
        if match: 
            self.header.date = match.group("date")
            if self.debug: print("HEADER-DATE: %s"%(self.header.date))

        RE_SOURCE = re.compile("Source\s+\"(?P<source>.*)\"\s*;")
        match = RE_SOURCE.search(value)
        if match: 
            self.header.source = match.group("source")
            if self.debug: print("HEADER-SOURCE: %s"%(self.header.source))
        """
        RE_HISTORY = re.compile("History\s+\{[.*\s\S]+\}")
        RE_ANN = re.compile("Ann\s*\{\*(?P<ann>.*)\*\}")
        match = RE_HISTORY.search(value)
        if match:
            anns = RE_ANN.findall(value)
            for ann in anns:
                self.header.history.append(ann.strip()) 

    def __signals_processor(self, value): 
        func = "%s.__signals_processor"%(self.__class__.__name__)
        if self.debug: print("DEBUG: %s: Starting ..."%(func)) 

        self.signals = SB.Signals() 


        # These will capture your basic signals: 
        RE_signal_In = re.compile("(?P<name>[\"\w\[\]\.]+)\s+In\s*;")
        RE_signal_Out = re.compile("(?P<name>[\"\w\[\]\.]+)\s+Out\s*;")
        RE_signal_InOut = re.compile("(?P<name>[\"\w\[\]\.]+)\s+InOut\s*;")
        RE_condensed_name = re.compile("(?P<base>[\"\w]+)\[(?P<num1>[\d]+)\.\.(?P<num2>[\d]+)\]")


     
        #RE_signal_withstuff = re.compile("(?P<name>[\w\[\]\.]+)\s+{(?P<details>[;\s\w\.]+)}")
        RE_signal_cb_ScanOut = re.compile("(?P<name>[\"\w\[\]\.]+)\s+Out\s*\{\s*ScanOut\s*;\s*\}")
        RE_signal_cb_ScanIn = re.compile("(?P<name>[\"\w\[\]\.]+)\s+In\s*\{\s*ScanIn\s*;\s*\}")

        # TODO: These should probably be moved to the SignalsBlock module (along with entire processing field huh) 


        # signals = SB.process(value)
        # for i in range(len(signals)): 
        #     self.signals.add(signals[i]) 


        match = RE_signal_cb_ScanOut.findall(value)
        if match: 
            for signal_in in match:  
                if '[' not in signal_in: 
                    self.signals.add(SB.Signal(name=signal_in, type = "Out", fields={"ScanOut":True}))
                elif '[' in signal_in: 
                    condensedName = RE_condensed_name.search(signal_in)
                    if not condensedName: 
                        raise RuntimeError("Should have found condensed name. ")
                    if condensedName: 
                        baseName = condensedName.group("base")
                        num1 = int(condensedName.group("num1"))
                        num2 = int(condensedName.group("num2"))
                        if num1 > num2: higher = num1; lower = num2
                        elif num2 > num1: higher = num2; lower = num1 
                        else:  raise RuntimeError("Numbers can equal each other.")
                        i = lower 
                        while i <= higher:
                            name = "%s[%d]"%(baseName,i) 
                            self.signals.add(SB.Signal(name=name, type = "Out", fields={"ScanOut":True}))
                            i += 1

        match = RE_signal_cb_ScanIn.findall(value)
        if match: 
            for signal_in in match:  
                if '[' not in signal_in: 
                    self.signals.add(SB.Signal(name=signal_in, type = "In", fields={"ScanIn":True}))
                elif '[' in signal_in: 
                    condensedName = RE_condensed_name.search(signal_in)
                    if not condensedName: 
                        raise RuntimeError("Should have found condensed name. ")
                    if condensedName: 
                        baseName = condensedName.group("base")
                        num1 = int(condensedName.group("num1"))
                        num2 = int(condensedName.group("num2"))
                        if num1 > num2: higher = num1; lower = num2
                        elif num2 > num1: higher = num2; lower = num1 
                        else:  raise RuntimeError("Numbers can equal each other.")
                        i = lower 
                        while i <= higher:
                            name = "%s[%d]"%(baseName,i) 
                            self.signals.add(SB.Signal(name=name, type = "In", fields={"ScanIn":True}))
                            i += 1

        # Basic In pins  
        match = RE_signal_In.findall(value)
        if match: 
            for signal_in in match:  
                if '[' not in signal_in: 
                    self.signals.add(SB.Signal(name=signal_in, type = "In"))
                elif '[' in signal_in: 
                    condensedName = RE_condensed_name.search(signal_in)
                    if not condensedName: 
                        raise RuntimeError("Should have found condensed name. ")
                    if condensedName: 
                        baseName = condensedName.group("base")
                        num1 = int(condensedName.group("num1"))
                        num2 = int(condensedName.group("num2"))
                        if num1 > num2: higher = num1; lower = num2
                        elif num2 > num1: higher = num2; lower = num1 
                        else:  raise RuntimeError("Numbers can equal each other.")
                        i = lower 
                        while i <= higher:
                            name = "%s[%d]"%(baseName,i) 
                            self.signals.add(SB.Signal(name=name, type = "In"))
                            i += 1
        match = RE_signal_Out.findall(value)
        if match: 
            for signal_in in match:  
                if '[' not in signal_in: 
                    self.signals.add(SB.Signal(name=signal_in, type = "Out"))
                elif '[' in signal_in: 
                    condensedName = RE_condensed_name.search(signal_in)
                    if not condensedName: 
                        raise RuntimeError("Should have found condensed name. ")
                    if condensedName: 
                        baseName = condensedName.group("base")
                        num1 = int(condensedName.group("num1"))
                        num2 = int(condensedName.group("num2"))
                        if num1 > num2: higher = num1; lower = num2
                        elif num2 > num1: higher = num2; lower = num1 
                        else:  raise RuntimeError("Numbers can equal each other.")
                        i = lower 
                        while i <= higher:
                            name = "%s[%d]"%(baseName,i) 
                            self.signals.add(SB.Signal(name=name, type = "out"))
                            i += 1
        match = RE_signal_InOut.findall(value)
        if match: 
            for signal_in in match:  
                if '[' not in signal_in: 
                    self.signals.add(SB.Signal(name=signal_in, type = "InOut"))
                elif '[' in signal_in: 
                    condensedName = RE_condensed_name.search(signal_in)
                    if not condensedName: 
                        raise RuntimeError("Should have found condensed name. ")
                    if condensedName: 
                        baseName = condensedName.group("base")
                        num1 = int(condensedName.group("num1"))
                        num2 = int(condensedName.group("num2"))
                        if num1 > num2: higher = num1; lower = num2
                        elif num2 > num1: higher = num2; lower = num1 
                        else:  raise RuntimeError("Numbers can equal each other.")
                        i = lower 
                        while i <= higher:
                            name = "%s[%d]"%(baseName,i) 
                            self.signals.add(SB.Signal(name=name, type = "InOut"))
                            i += 1

                        self.signals.add_shorthand_ref(signal_in) # NOTE: Add short hand reference
        return 

    def __signalgroups_processor(self, value): 
        pass 

    def __in_free_state(self): 
        return self.__states["FREE"]

    def __new_top_level_state(self, value): 
        if value not in self.TOPLEVEL.keys(): 
            raise RuntimeError("Must be top level state: ", value) 
        self.__states[value] = True
        self.__states["FREE"] = False
        self.__current_state = value
    
    def __close_current_state(self):
        self.__states[self.__current_state] = False
        self.__states["FREE"] = True
        self.__current_state = "FREE"

    def __get_current_state(self): 
        return self.__current_state

    def __current_state_ends_on_semicolon(self):
        if self.TOPLEVEL[self.__current_state]["ending"] == ";":
            return True
        else: return False 

    def __eat(self, value):
        self.TOPLEVEL[self.__current_state]["processor"](value)


    def parse(self,):
        """ 

        The implementation is made difficult due to the fact that: 
            - it is single pass (with sub multi-passes)
            - it processes the file in a line and character fashion.

        There is basically : 
          - Dont get caught in a string-lteral. 
          -  We implement look-back methodolgies (we track the last char)
        """
        debug = self.debug
        identifier = []
        cbs = 0
        start_curly_found  = 0
        end_curly_found  = 0
        skipline = False 
        blockcomment = False
        lastchar = ''
        with open(self.sfp,"r") as sfd: 
            for i, line in enumerate(sfd, start=1):
                for j, char in enumerate(line, start=0):
                    if debug: print("CHAR: %s"%(char))



                    if blockcomment: 
                        if char == "*" and lastchar == "/": # Nest block? Error if so . 
                            print("Nest block..... Illegal %s"%(line))
                            sys.exit(1)
                        if char == "/" and lastchar == "*": 
                            if debug: print("DEBUG: Block comment terminated")
                            blockcomment = False  
                        continue

                    if char == "/" and lastchar == "/": 
                        if debug: print("INLINE COMMENT FOUND %s"%(line))
                        # NOTE: If inline comment, skip the rest of the line.
                        skipline = True
                    
                    # Freelance: Start of block  
                    if char == "*" and lastchar == "/": 
                        if debug: print("DEBUG: BLOCK COMMENT FOUND %s"%(line))
                        blockcomment = True
                        lastchar = char
                        continue # NOTE: IF you skip line while in if-branch, you must store last char

                    # ------------------------------------------------------------------------------------




                    # This is an important block here.... 
                    #   - the last char gets stored, 
                    #   - a sneaky look-ahead is used for finding inline comments
                    #   - the current char is stored in the 'identifier' list. 
                    # 
                    # Thus the implication is that later code `~simply` worry about state. 
                    #
                    lastchar = char  # TODO: This seems like an improper spot to set the lastchar.
                    if skipline: 
                        skipline = False 
                        break 
                    elif char == "/" and self.__in_free_state(): 
                        try : 
                            if line[j+1] == "/":  # We found inline comment
                                break  
                        except:
                            raise RuntimeError("Recieved weird line: %s"%(line)) 
                        print("XXXXXXXXXXX Should never see this line...")
                    else: 
                        identifier.append(char)

                    # Count the curlies
                    if char == "{":
                        cbs +=1 
                        if cbs == 1: start_curly_found = 1
                    if char == "}": 
                        cbs -= 1
                        if cbs == 0: end_curly_found = 1

                    if self.__in_free_state(): 
                        if char in whitespace_character or cbs == 1: 
                            value = "".join(identifier).strip("{} \n") # NOTE: 'identifer' is not resest! 
                            if value : # Meaning we have have stored actual chars, then flag the start state
                                self.__new_top_level_state(value)
                                continue
                            else: pass 
                    else: 
                        if char == ";": 
                            if self.__current_state_ends_on_semicolon():
                                self.__eat("".join(identifier))
                                self.__close_current_state()
                                identifier = []
                            else: pass
                        elif end_curly_found: 
                            self.__eat("".join(identifier))
                            self.__close_current_state()
                            identifier = []
                            start_curly_found = 0
                            end_curly_found = 0
                        else:  # Else, continue becasue 'char' was just a char.
                            continue

        return 




if __name__ == "__main__": 
    print("PySTIL.stil running ... \n")

    if "-debug" in sys.argv: debug = True
    else: debug = False 
    so = STIL(sfp=sys.argv[-1], debug=debug)
    so.parse()

    print("")
    print("STIL %s;"%(so.stil_version), "\n")
    print(so.header, "\n")
    print(so.signals, "\n")





    print(utils.greetings())