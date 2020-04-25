import sys, os, re

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

    def __str__(self):
        ret_str = ["Header { \n"]
        if self.title: 
            ret_str.append("  Title \"%s\";\n"%(self.title))
        if self.date: 
            ret_str.append("  Date \"%s\";\n"%(self.date))
        if self.source: 
            ret_str.append("  Source  \"%s\";\n"%(self.source))
        if self.history:
            for ann in self.history: 
                ret_str.append("    {* " + ann +"*}\n")
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
        print("STIL STATEMENT: recieved: ", value)
        RE_STIL_VERSION = re.compile("STIL\s+(?P<version>[\d\.]+)\s*;")
        match = RE_STIL_VERSION.search(value)
        if match: 
            self.stil_version = match.group("version")
            print("SITL VERSION: %s"%(self.stil_version))

    def __header_processor(self, value): 
        print("Header STATEMENT: recieved: ", value)

        self.header = Header()

        RE_TITLE = re.compile("Title\s+\"(?P<title>.*)\"\s*;")
        match = RE_TITLE.search(value)
        if match: 
            self.header.title = match.group("title")
            print("HEADER-TITLE: %s"%(self.header.title))
    
        RE_DATE= re.compile("Date\s+\"(?P<date>.*)\"\s*;")
        match = RE_DATE.search(value)
        if match: 
            self.header.date = match.group("date")
            print("HEADER-DATE: %s"%(self.header.date))

        RE_SOURCE = re.compile("Source\s+\"(?P<source>.*)\"\s*;")
        match = RE_SOURCE.search(value)
        if match: 
            self.header.source = match.group("source")
            print("HEADER-SOURCE: %s"%(self.header.source))
        
        RE_HISTORY = re.compile("History\s+\{[.*\s\S]+\}")
        RE_ANN = re.compile("Ann\s*\{\*(?P<ann>.*)\*\}")
        match = RE_HISTORY.search(value)
        if match:
            anns = RE_ANN.findall(value)
            for ann in anns:
                print(ann) 
                self.header.history.append(ann) 

    def __signals_processor(self, value): 
        pass 

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
                    print("CHAR: %s"%(char))
                    if blockcomment: 
                        if char == "*" and lastchar == "/": # Nest block? Error if so . 
                            print("Nest block..... Illegal %s"%(line))
                            sys.exit(1)
                        if char == "/" and lastchar == "*": 
                            print("DEBUG: Block comment terminated")
                            blockcomment = False  
                        continue

                    if char == "/" and lastchar == "/": 
                        print("INLINE COMMENT FOUND %s"%(line))
                        # NOTE: If inline comment, skip the rest of the line.
                        skipline = True
                    
                    # Freelance: Start of block  
                    if char == "*" and lastchar == "/": 
                        print("DEBUG: BLOCK COMMENT FOUND %s"%(line))
                        blockcomment = True
                        lastchar = char
                        continue # NOTE: IF you skip line while in if-branch, you must store last char

                    # ------------------------------------------------------------------------------------
                    lastchar = char   
                    if skipline: 
                        skipline = False 
                        break 
                    elif char == "/" and self.__in_free_state(): 
                        continue 
                    else: identifier.append(char)

                    if char == "{":
                        cbs +=1 
                        if cbs == 1: start_curly_found = 1
                    
                    if char == "}": 
                        cbs -= 1
                        if cbs == 0: end_curly_found = 1

                    if self.__in_free_state(): 
                        if char in whitespace_character or cbs == 1: 
                            value = "".join(identifier).strip("{} \n") 
                            print("We are the start of a top leve section: ",value)
                            if value : # Meaning we have have stored actual chars, then flag the start state
                                self.__new_top_level_state(value)
                                continue
                            else: 
                                print("LOL have stored only whitespace")
                    elif not self.__in_free_state(): 
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
        return 




if __name__ == "__main__": 
    print("PySTIL.stil running ... \n")
    so = STIL(sfp=sys.argv[-1])
    so.parse()

    print("")
    print("STIL %s;"%(so.stil_version))
    print(so.header)