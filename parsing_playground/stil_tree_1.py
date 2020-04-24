import os, sys, re

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


class Signal(object): 
    def __init__(self,*args,**kwargs):
        if "name" in kwargs: self.name = kwargs["name"]
        else: self.name = ""

        if "type" in kwargs: self.type = kwargs["type"]
        else: self.type = ""

        if "extra" in kwargs: self.extra = kwargs["extra"].strip()
        else: self.extra= ""
        # ^^^ TODO: Need to parse this down into a series of flags.

    def get_name(self,):
        return self.name 

    def get_type(self,):
        return self.type

    def __str__(self): 
        ret_str = ["%s %s"%(self.name,self.type)]
        if self.extra: 
            ret_str.append(" { %s }\n"%(self.extra))
        elif not self.extra: 
            ret_str.append(";\n")
        # ^^^ TODO: After fixing the self.extra will be have to change the the printing here. 
        return "".join(ret_str)



class Signals(object): 

    def __init__(self, *args, **kwargs):
        self.__map = {}

    def add(self, signal):
        if not isinstance(signal, Signal): 
            raise ValueError("Add must be of  type Signal")
        else: 
            self.__map[signal.get_name()] = signal
            # ^^^ NOTE: I am assuiming all signal names must be uunique

    def __str__(self): 
        ret_str = ["Signals {\n"]
        for i, name in enumerate(self.__map.keys()): 
            #ret_str.append("  %s %s"%(name, self.__map[name].get_type()))
            ret_str.append("  " + str(self.__map[name]))
            
        
        ret_str.append("}\n")
        return "".join(ret_str)
        
            

class STILTree(object): 

    def __init__(self,*args,**kwargs): 
        if "debug" in kwargs: self.debug = kwargs["debug"]
        else: self.debug = None 

        self.__CID = 0
        self.__PID = 0  

        self.__map = {}
        # ^^ this map will be filled with 

        self.__states = {
            "FREE"    : True, 
            "STIL"    : False, 
            "Header"  : False, 
            "Title"   : False, 
            "Date"    : False, 
            "Source"  : False, 
            "History" : False, 
            "Ann"     : False,
        }
        self.__states_queue = []

        self.TOPLEVEL = {
            "STIL" : ";", 
            "Header" : "}",
            "Signals" : "}",
        }
        self.__TOPLEVEL_CALLBACKS = {
            "STIL": self.__stil_statement,
            "Header" : self.__header_statement, 
            "Signals" : self.__signals_statement, 
        }


        self.stil_version = ""
        self.header = None
        self.signals = None

    def in_free_state(self): 
        return self.__states["FREE"]

    def new_top_level_state(self, value): 
        if value not in self.TOPLEVEL.keys(): 
            raise RuntimeError("Must be top level state: ", value) 
        self.__states[value] = True
        self.__states["FREE"] = False
        self.__current_state = value
    
    def close_current_state(self):
        self.__states[self.__current_state] = False
        self.__states["FREE"] = True

    def get_current_state(self): 
        return self.__current_state

    def current_state_ends_on_semicolon(self):
        if self.TOPLEVEL[self.__current_state] == ";":
            return True
        else: return False 

    def eat(self, value):
        self.__TOPLEVEL_CALLBACKS[self.__current_state](value)
    
    def __stil_statement(self, value): 
        print("STIL STATEMENT: recieved: ", value)
        RE_STIL_VERSION = re.compile("STIL\s+(?P<version>[\d\.]+)\s*;")
        match = RE_STIL_VERSION.search(value)
        if match: 
            self.stil_version = match.group("version")
            print("SITL VERSION: %s"%(self.stil_version))
        

    def __header_statement(self, value): 
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
        
    def __signals_statement(self, value): 
        print("Signals STATEMENT: %s"%(value))

        self.signals = Signals()

        RE_SIGNAL_SEMICOLON = re.compile("(?P<name>[\w\.\[\]]+)\s+(?P<type>[\w]+)\s*;")
        RE_SIGNAL_W_BRACKETS = re.compile("(?P<name>[\w\.\[\]]+)\s+(?P<type>[\w]+)\s*\{(?P<extra>[\w\d\s;]+)\}")
        # ^^^ TODO: Can you have multiple identifiers in the extra? ex. ScanIn and TerminateLow? 
        signal_semi = RE_SIGNAL_SEMICOLON.findall(value)
        signal_wbrackets = RE_SIGNAL_W_BRACKETS.findall(value)
        if signal_semi:
            for signal in signal_semi: 
                #print(signal.group("name"),signal.group("type"))
                name = signal[0]
                _type = signal[1]
                RE_CONDENSE_SIGNAL = re.compile("[\w]+\[(?P<start>[\d]+)\.\.(?P<end>[\d]+)\]")
                condensed_signals = RE_CONDENSE_SIGNAL.search(name)
                if not condensed_signals: 
                    self.signals.add(Signal(name=name, type=_type))
                if condensed_signals:
                    _name = name.split("[")[0]
                    _start = condensed_signals.group("start")
                    _end = condensed_signals.group("end")
                    list_of_values = [_start, _end]
                    list_of_values.sort()
                    for i in range(int(list_of_values[0]), int(list_of_values[-1]) + 1):
                        self.signals.add(Signal(name=_name+"["+str(i)+"]", type=_type ))
        if signal_wbrackets: 
            for signal in signal_wbrackets:
                print("MATCH: ", signal)
                name = signal[0]
                _type = signal[1]
                extra = signal[2]
                RE_CONDENSE_SIGNAL = re.compile("[\w]+\[(?P<start>[\d]+)\.\.(?P<end>[\d]+)\]")
                condensed_signals = RE_CONDENSE_SIGNAL.search(name)
                if not condensed_signals: 
                    self.signals.add(Signal(name=name, type=_type, extra = extra))
                if condensed_signals:
                    _name = name.split("[")[0]
                    _start = condensed_signals.group("start")
                    _end = condensed_signals.group("end")
                    list_of_values = [_start, _end]
                    list_of_values.sort()
                    for i in range(int(list_of_values[0]), int(list_of_values[-1]) + 1):
                        self.signals.add(Signal(name=_name+"["+str(i)+"]", type=_type, extra = extra ))






class STILNode(object): 
    def __init__(self,*args, **kwargs): 
        if "debug" in kwargs: self.debug = kwargs["debug"]
        else: self.debug = None 

    

        


    


def parse(sfp, ): 


    string_literal = False 
    identifier = []
    lastchar = ''


    stiltree = STILTree()

    cbs = 0
    start_curly_found  = 0
    end_curly_found  = 0


    with open(sfp,"r") as sfd: 
        for i, line in enumerate(sfd, start=1):
            if i == 99: break
            for j, char in enumerate(line, start=0):
                print("CHAR: %s"%(char))
                # ----------------------------------------------------- S: String-literal
                #if string_literal: 
                #    if char == "\"" and lastchar != "\\": # Closing string-literal
                #        identifier.append(char)
                #        _str = "".join(identifier); identifier = []
                #        string_literal = False
                #        continue 
                #    else: 
                #        identifier.append(char)
                #        continue 
                # ----------------------------------------------------- Freelance: String-literal start. 
                #if char == "\"":  # TODO: could ad 'and state["notdone"]'
                #    string_literal = True
                #    identifier.append(char)
                #    continue


                # ------------------------------------------------------------------------------------
                identifier.append(char)
                #print(identifier)

                if char == "{":
                    cbs +=1 
                    if cbs == 1: start_curly_found = 1
                    
                if char == "}": 
                    cbs -= 1
                    if cbs == 0: end_curly_found = 1

                if stiltree.in_free_state(): 
                    if char in whitespace_character or cbs == 1: 
                        value = "".join(identifier).strip("{} \n") 
                        print("We are the start of a top leve section: ",value)
                        if value : # Meaning we have have stored actual chars, then flag the start state
                            stiltree.new_top_level_state(value)
                            continue
                        else: 
                            print("LOL have stored only whitespace")
                elif not stiltree.in_free_state(): 
                    if char == ";": 
                        if stiltree.current_state_ends_on_semicolon():
                            stiltree.eat("".join(identifier))
                            stiltree.close_current_state()
                            identifier = []
                        else: pass
                    elif end_curly_found: 
                        stiltree.eat("".join(identifier))
                        stiltree.close_current_state()
                        identifier = []
                        start_curly_found = 0
                        end_curly_found = 0

                lastchar = char   

    return stiltree
        


if __name__ == "__main__": 
    print("Main")


    so = parse(sys.argv[-1])

    print(so.stil_version)
    print(so.header)
    print(so.signals)