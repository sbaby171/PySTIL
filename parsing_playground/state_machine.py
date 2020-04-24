import os, sys

""" 
I basically got over this becasue it wasnt a good approach to handle recursion. 
Bacislly,, nested nested nested etc. would be difficult to implement on this. 
"""


#IDENTIFIER = "identifier"
#NUMBER = "number"
#STRING = "string-literal"
SEMICOLON = "semicolon"
STARTCURLY = "startcurly"
ENDCURLY = "endcurly"
ENTITY = "entity"



class Annotation(object): 
    def __init__(self, *args, **kwargs): 
        self.value = ""

    def set_value(self,value): 
        self.value = value 
    
    def incoming(self, value): 
        print("TODO: annocation")

class Header (object): 
    """ 

    From the STIL documentation. 
    
        9.0 Header Block: 

        The Header block may appear only once at the beginning of a STIL file, and is used to 
        specify data that pertains to the creation of the file. 

        9.1 Header Block Syntax: 

            Header {
                (Title "TITLE_STRING";)
                (Date "DATE_STRING";)
                (Source "SOURCE_STRING";)
                (HISTORY {} )
            }

            Header: Start of the header block 

            Title String used to identify this STIL block or file. 

            Date: ....

            Source: A special annotiation used to indicate how and/or where the file was generated. 

            History: A block used to contain annotations as the history of the data in the file. 

    """

    def __init__(self, *args, **kwargs): 
        self.title = ""
        self.date = ""
        self.source = ""
        self.history = [] # List of Annotations...
        self.fields = {
            "Title"  :  False, 
            "Date"   :  False,
            "Source" :  False,
            "History":  False,
            "Ann"    :  False,
        }
        self.__field_queue = []
        self.__done = False 

    def next_field(self, field):
        func = "%s.next_field"%(self.__class__.__name__)
        self.fields[field] = True
        self.__field_queue.append(field)
        print("DEBUG: (%s): Set the following field to on: %s"%(func, self.__field_queue[-1]))

    def close_field(self):
        if len(self.__field_queue) == 0: # No queued up fields, the entire section is done 
            self.__done == True
        else: 
            closing_field = self.__field_queue[-1]
            self.fields[closing_field] = False
            del self.__field_queue[-1]
            self.__done == False
        return self.__done 

    def open(self,): 
        if len(self.__field_queue) == 0: 
            return True
        else : return False 
        

    def value(self, _value): 
        func = "%s.value"%(self.__class__.__name__)
        print(self.__field_queue)
        if self.__field_queue[-1] == "Title": 
            self.title = _value
            print("DEBUG: (%s): Header.title set: %s"%(func, self.title))
        elif self.__field_queue[-1] == "Date": 
            self.date = _value
            print("DEBUG: (%s): Header.date set: %s"%(func, self.title))
        elif self.__field_queue[-1] == "Source": 
            self.source = _value
            print("DEBUG: (%s): Header.source set: %s"%(func, self.source))
        elif self.__field_queue[-1] == "History": 
            if _value != "Ann": 
                raise RuntimeError("Must recieve 'Ann' value within Header.history")
            else: 
                self.history.append(Annotation())
        elif self.__field_queue[-1] == "Ann": 
            self.history[-1].incoming(_value)
        else: 
            print("NOT SUREEEE")


    
    def __str__(self): 
        ret_str = ["Header Instance:\n"]
        ret_str.append("  Title   : %s\n"%(self.title))
        ret_str.append("  Date    : %s\n"%(self.date))
        ret_str.append("  Source  : %s\n"%(self.source))
        ret_str.append("  History : %s\n"%(self.history))
        return "".join(ret_str)
         

STIL_VERSION = ""
HEADER = Header()

class StateMachine(object): 

    def __init__(self,*args,**kwargs): 
        self.debug = False 

        self.states = {
            "free": True,
            "string-literal": False, 

            "STIL" : False,
            "Header" : False,
        }
        self.__last_opened_state = ""

        self.TOPLEVEL = {
            "STIL" : "", 
            "Header" : "",
        }
        self.STILBLOCK_CALLBACKS = {
            "STIL" : self._stil_statement , 
            "Header" : self._header_statement, 
        }




    def incoming(self, TYPE, VALUE, ): 
        """ 
        TYPE : global variables.
            SEMICOLON  : A semicolon ';' was found in main parser. 
            STARTCURLY : A starting curly brace '{' was found in main parser. 
            ENDCURLY   : An ending curly brace '}' was found in main parser. 
            ENTITY     : A non-terminating (or starting) signal coming from main. 

        VALUE : Collected string. 
            This the the string as collected during the main parser. 
        """
        func = "%s.incoming"%(self.__class__.__name__)

        print("DEBUG: (%s): Incoming-value(type=%s): %s"%(func, TYPE, VALUE))

        if TYPE == SEMICOLON and self.states["free"]: 
            raise RuntimeError("Error: Cant have start/end signals while in free state")
        if TYPE == STARTCURLY and self.states["free"]: 
            raise RuntimeError("Error: Cant have start/end signals while in free state")
        if TYPE == ENDCURLY and self.states["free"]: 
            raise RuntimeError("Error: Cant have start/end signals while in free state")

        if self.states["free"]: 
            if VALUE not in self.TOPLEVEL.keys(): 
                raise RuntimeError("%s: Received non Top-Level Idneitifer while in Free state: %s"%(func, VALUE))
            self.set_state(VALUE, True)
            self.set_state("free", False)

            print("DEBUG: (%s): Top-Level Section is set to True: %s"%(func, self.get_current_state()))
            return

        if not self.states["free"]: 
            self.STILBLOCK_CALLBACKS[self.get_current_state()](TYPE=TYPE, VALUE=VALUE)





    def __getitem__(self, state): 
        if state not in self.states: 
            raise ValueError("State '%s' is not supported."%(state))

        return self.states[state]

    def set_state(self, state, status): 

        if state not in self.states: 
            raise ValueError("State '%s' is not supported."%(state))

        ## If free ON, then everything else must be off. Converse is also true.
        #if ((state != "free") and (status not in [ [],"", None, 0, 0.0])): 
        #    print("Non free states with a non-zero status: %s : %s"%(state, status))
        #    self.states["free"] = False
        #    self.__last_opened_state = state
        #else: 
        #    self.states["free"] = True
        #   self.__last_opened_state = ""
        # ^^^ NOTE: The work above is wrong because it is trying to do too much. 
        #     this function shouldnt be making inferences or implications as to  
        #     which states should be opened or closed. It shoud maintain a single 
        #     respsonsibility and that is to set that the state provided to it.
        #     It shoud be the job of the caller to mange the logic and call this 
        #     however many times neeced. 
        if status: 
            self.__last_opened_state = state
        self.states[state] = status


    def get_current_state(self): 
        return self.__last_opened_state





    def _stil_statement(self, TYPE, VALUE): 
        """
        Taking in the following identifier: 
            VALUE  the stil version number. 
            SEMICOLON: Semicolon
        """
        global STIL_VERSION
        func = "%s._stil_statement"%(self.__class__.__name__)
        print("DEBUG: (%s): Invoked..."%(func))

        if TYPE == SEMICOLON: 
            self.set_state("STIL", False)
            self.set_state("free", True)
            print("DEBUG: (%s): Closing the 'STIL' section. Going back to Free state."%(func))
        elif TYPE == ENTITY: 
            STIL_VERSION = VALUE
            print("DEBUG: (%s): STIL version: %s"%(func, STIL_VERSION))
        return  



    def _header_statement(self, TYPE, VALUE): 
        """ 
        Taking in the following tokens: 
            NAME: Name of 
        """
        func = "%s._header_statement"%(self.__class__.__name__)
        print("DEBUG: (%s): Invoked..."%(func))

        if TYPE == STARTCURLY: 
            pass
        elif TYPE == ENDCURLY or TYPE == SEMICOLON: 
            if HEADER.close_field() : 
                self.set_state("Header", False) 
                self.set_state("free", True)

        elif TYPE == ENTITY and HEADER.open(): 
            if VALUE == "Title":
                HEADER.next_field("Title")
            elif VALUE == "Date":
                HEADER.next_field("Date")
            elif VALUE == "Source":
                HEADER.next_field("Source")
            elif VALUE == "History": 
                HEADER.next_field("History")
            elif VALUE == "Ann": 
                HEADER.next_field("Ann")
            else: 
                raise RuntimeError("%s: Received invalid keyword within Header section: %s"%(func,VALUE))
        elif TYPE == ENTITY and not HEADER.open():  
            HEADER.value(VALUE)
        else: pass 




    
        return 



            




whitespace_character = [" ", "\t", "\n"]

class Parser(object): 


    def __init__(self, sfp):
        if not os.path.isfile(sfp):
            raise ValueError("File does not exist.")
        else: self.sfp = sfp

    def parse(self, *args, **kwargs): 

        state = StateMachine()
        identifier = []
        cbs = 0



        string_literal = False 
        with open(self.sfp,"r") as sfd: 
            for i, line in enumerate(sfd, start=1):
                if i == 11: break

                for j, char in enumerate(line, start=0):
                    print("CHAR: %s"%(char))
                    # ----------------------------------------------------- S: String-literal
                    if string_literal: 
                        if char == "\"" and lastchar != "\\": # Closing string-literal
                            identifier.append(char)
                            _str = "".join(identifier); identifier = []
                            state.incoming(TYPE = ENTITY, VALUE = _str)
                            # NOTE: The point here is once an identifier is established, we 
                            # call the StateMachine to handle, RATHER than needing to always go 
                            # to the end of the for-loop. This is like a 'goto' or 'jumpto' 
                            # functionality. 
                            string_literal = False
                            continue 
                        else: 
                            identifier.append(char)
                            continue 
                    # ----------------------------------------------------- Freelance: String-literal start. 
                    if char == "\"":  # TODO: could ad 'and state["notdone"]'
                        #state.set_state("string-literal", True)
                        string_literal = True
                        identifier.append(char)
                        continue
                    # Checking for termination or section starters. 
                    if char ==  "{" : 
                        state.incoming(TYPE = STARTCURLY, VALUE = char); cbs += 1
                        continue 
                    if char ==  "}" : 
                        value = "".join(identifier); identifier = []
                        if value: 
                            state.incoming(TYPE = ENTITY, VALUE = value)
                        state.incoming(TYPE = ENDCURLY, VALUE = char); cbs -= 1
                        continue 
                    if char == ";": 
                        value = "".join(identifier); identifier = []
                        if value: 
                            state.incoming(TYPE = ENTITY, VALUE = value)
                        state.incoming(TYPE = SEMICOLON, VALUE = char)
                        continue 
                    # ^^^ NOTE: Rather than store this the curly brace in the identifier, we should 
                    #     be sending a 'START-SIGNAL' to the StateMachine indicating a new section is 
                    #     starting. This could be a top- or nontop-level section. StateMachine can 
                    #     then propagate the 'START-SIGNAL' to the which ever state is running. 
                    lastchar = char   
                    if char not in whitespace_character: 
                        identifier.append(char)
                    else: 
                        if len(identifier) == 0: continue 
                        value = "".join(identifier); identifier = []
                        state.incoming(TYPE = ENTITY, VALUE = value)
                        #state.new_identifer(_iden, IDENTIFIER, cbs)
                        # NOTE: The key here is that the identifier can be a STIL keyword, 
                        # a single quote, a curly brace, or semicolon. It is then up to the 
                        # StateMachine to parse the rest. 
        




if __name__ == "__main__": 
    pso = Parser(sys.argv[-1])


    pso.parse()

    
    print("STIL-VERSION: %s"%(STIL_VERSION))
    print(HEADER)


