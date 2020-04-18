import sys, os, argparse 



def greeetings():
    print("Hello World from stil.")
    return 




# TODO: As with most parsing implementations, you always have to ask
# yourself, "Am I in a comment or string literal", and of course there
# are can be many forms of either. 
# 
# One way I want to implement this may be to handle it is char by char. 
# We collect the chars and upon a *group* we identifer which group it 
# is.  


# ---------------------------------------------------------------------.......-
# See section 6.8: 


special_character = ["!","@","#","$","%","^","&","*","(",")","-","+","=",
                     "|","`","{","[","}","]",":",";","'",",","<",".",".",
                     ">","/","?","\\",
                    ]
whitespace_character = [" ", "\t", "\n"]


# See section 6.12: Number characteristics: 
digit = ['0','1','2','3','4','5','6','7','8','9','0']

# ---------------------------------------------------------------------.......-
class STILParser(object): # STILWriter
    def __init__(self, sfp,**kwargs):
        if "debug" in kwargs: self.debug = kwargs["debug"]
        else: self.debug = 0

        if not os.path.isfile(sfp): 
            raise ValueError("STIL doesn't exist or has bad permissions:"\
                " %s" %(sfp))
        else: self.stil_path = sfp

        self.stil_version = ""
        self.parsed = self.parse()
  
        if self.debug: 
            print("DEBUG: Create %s instance"%(self.__class__.__name__))
            print("DEBUG:   - stil_path: %s"%(self.stil_path))
            if self.stil_version: 
                print("DEBUG:   - stil_version: %s"%(self.stil_version))

    def parse(self,):
        func = "%s.parse"%(self.__class__.__name__)
        print("TODO: %s"%(func))


        charcount = 0
        linecount = 0 
        lastchar  = ''
        identifier = []
        cbs = 0

        endswith_semicolon = False


        state = {
            "string-literal" : False,
            "skipline": False, 
            "blockcomment" : False,
            "free"  : True, # Indicates we are not in any STIL block 
            "STIL" : False,
        }
        holder = []
        with open(self.stil_path,"r") as sfd: 
            for i, line in enumerate(sfd, start=1):
                if i == 11: break

                for j, char in enumerate(line, start=0):
                    print("CHAR: %s"%(char))
                    #if char in whitespace_character: print(" SPACE ")


                    # ----------------------------------------------------- S: String-literal
                    if state["string-literal"]: 
                        if char == "\"" and lastchar != "\\": # Closing string-literal
                            identifier.append(char)
                            state["string-literal"] = True 
                            print("Found string-literal: %s"%("".join(identifier)))
                            identifier = []
                            state["string-literal"]: False
                            lastchar=char; continue
                        else: 
                            identifier.append(char)
                            lastchar=char; continue

                    # ----------------------------------------------------- S: '/*' Block comment
                    if state["blockcomment"]: 
                        if char == "*" and lastchar == "/": # Nest block? Error if so . 
                             print("Nest block..... Illegal %s"%(line))
                             sys.exit(1)
                        if char == "/" and lastchar == "*": 
                            print("DEBUG: Block comment terminated")
                            state["blockcomment"] = False 
                        continue

                    # NOTE: My thoughts rn are to have the string-literal and commnent section
                    #       states checked before anything else. Why? Because you might mis count 
                    #       a character. What is a curly-braces is within an aforementioned entity 
                    #       then you might miscount. This could be addresseed by placing the state
                    #       checks within the if branch, but that is tedious and complex. So what 
                    #       is the tradeoff? That ordering of the code is very important. 

                    # QUES: What terminates the 'section' or block in STIL? I thinks its either a 
                    #       semicolon OR a closing bracket.
                    # ANSW: Correct. See 7.0 of STIL documentation. 

                    if char == "{": cbs += 1
                    if char == "}": cbs -= 1
                    # Check the curly brace stuff. 
                


                    # Freelance: Start of string-literal
                    if char == "\"":  # TODO: could ad 'and state["notdone"]'
                        state["string-literal"] = True
                        state["skipline"] = False
                        pass
                    # ^^^ TODO: What about single quotation marks.
                    #           A: According to Section 6.4 Table-2, "single quote character
                    #           is used to denote timing and signal expressions."
                    # ^^^ NOTE: Once you have the complete string-literal its placement or 
                    #            association is dependent on the context at that time.

                    # Freelance: Start '//' inline comment
                    if char == "/" and lastchar == "/": 
                        print("INLINE COMMENT FOUND %s"%(line))
                        # NOTE: If inline comment, skip the rest of the line.
                        state["skipline"] = True
                    
                    # Freelance: Start of block  
                    if char == "*" and lastchar == "/": 
                        print("DEBUG: BLOCK COMMENT FOUND %s"%(line))
                        state["blockcomment"] = True
                        lastchar = char
                        continue # NOTE: IF you skip line while in if-branch, you must store last char

                    

                    #print("LAST CHAR-LOOP INSTANCE")
                    lastchar = char
                    if state["skipline"]: 
                        state["skipline"] = False 
                        lastchar = '' 
                        break 




                    
                    # Freelance: Storing characters. clear
                    
                    if char not in whitespace_character: 
                         identifier.append(char)
                    else: 
                        holder.append("".join(identifier))
                        print("DEBUG: FOUND IDENTIFIER: %s"%(holder[-1]))
                        identifier = []
                        if holder[-1] == ';': 
                            endswith_semicolon = True 
                        else: 
                            print("\t doesnt end in ';'")
                            endswith_semicolon = False 


                    # state.free() 
                    #   True  : Freelance section, the identifier must a STIL keyword 
                    #   False : We are in STIL block. 
                    # 
                    # state.pattern()
                    #   True  : Pattern STIL block. This should be the first check 
                    #           because most of a STIL in in a pattern block  
                    #   False : Not in pattern block. 
                    # 
                    if state["free"]: # If free the Identifier my 
                        if len(holder) == 0: continue 
                        if holder[-1] == "STIL": 
                            print("DEBUG: 'STIL' statement found")
                            state["STIL"] = True
                            state["free"] = False 
                            holder = []; identifier = []
                            continue 
                    elif state["STIL"]: 
                        if endswith_semicolon: 
                            if len(holder) == 2: 
                                self.stil_version = holder[0]
                            elif len(holder) == 1:
                                self.stil_version = holder[0][:-1]
                            else: 
                                raise RuntimeError("Bad syntax for STIL statement: %s"%(holder))
                            state["STIL"] = False 
                            state["free"] = True
                            endswith_semicolon = False 
                        else: 
                            lastchar = char; continue 








        return True


def load(stil, debug=False): 
    return STILParser(stil,debug=debug)
        
def __cli():
    func = "__cli"
    parser = argparse.ArgumentParser()
    
    # Default settings: 
    # -----------------
    parser.add_argument("-debug", help="increase output verbosity.",
                         action="store_true") 
    # ^^^ TODO: This forces the debug value to be boolean. 


    # STIL files: 
    # -----------------
    parser.add_argument("stil", metavar="STIL", type=str,
                         help="Stil file to be translated")

    args = parser.parse_args()

    # Sanity Checks: 
    # -----------------
    if args.debug: 
        print("DEBUG: (%s): Command-line-arg-settings:"%(func))
        print("DEBUG: (%s):   - %s "%(func,args))


    return args        


if __name__ == "__main__": 
    print("STIL - MAIN.")

    args = __cli()

    spo = load(args.stil, args.debug)


"""
STIL 1.0;

Header {
   Title "Simple 74act299 Example for STIL Reader";
   Date "Mon Aug 29 08:00:00 2005";
   Source "Hand Generated";
   History {
      Ann {* Mon Aug 29 08:00:00 2005 -- Initial Revision *}
   }
}

Signals {
  CP In; MR In; S0 In; S1 In; D0 In {ScanIn;} D7 In;
  Q0 Out; Q7 Out {ScanOut;} IO[0..7] InOut;
}

SignalGroups {
  Bus = 'IO[0..7]';
}

Timing {
  WaveformTable WavTbl1 {
    Period '100ns';
    Waveforms {
	CP 	{ P  { '0ns' D;   '50ns' U; } }
	MR 	{ 01 { '0ns' D/U; '20ns' U; } }
	S0	{ 01 { '0ns' D/U; } }
	S1	{ 01 { '0ns' D/U; } }
	D0	{ 01 { '0ns' D/U; } }
	D7	{ 01 { '0ns' D/U; } }
	Q0 	{ LH { '80ns' L/H; } }
	Q7 	{ LH { '80ns' L/H; } }
	Bus     { 01 { '30ns' D/U; } 
	          LH { '80ns' L/H; } }
    }
  }
}

PatternBurst Burst1 {
  PatList {
    Pat1;
  }
}

PatternExec Exec1 {
  PatternBurst Burst1;
}


Pattern Pat1 { 
  W WavTbl1;
  Ann {* Reset *}
  V { CP=P; MR=0; S1=0; S0=0; D0=0; D7=0; Q0=L; Q7=L; }  // Vec 0
  Ann {* Hold 00000000 *}
  V { CP=P; MR=1; Q0=L; Q7=L; Bus=LLLLLLLL; }            // Vec 1
  Ann {* Hold 00000000 *}
  V { }                                                  // Vec 2
  Ann {* Hold 00000000 *}
  V { }                                                  // Vec 3
  Ann {* Load 11001111 *}
  V { CP=P; S1=1; S0=1; Q0=H; Q7=H; Bus=11001111; }      // Vec 4
  Ann {* Hold 11001111 *}
  V { CP=P; S1=0; S0=0; Q0=H; Q7=H; Bus=11001111; }      // Vec 5
  Ann {* Reset *}
  V { CP=P; MR=0; S1=0; S0=0; D0=0; D7=0; Q0=L; Q7=L; }  // Vec 6
  Ann {* Load 11111111 *}
  V { CP=P; S1=1; S0=1; Q0=H; Q7=H; Bus=HHHHHHHH; }      // Vec 7
  Ann {* Shift 0R *}
  V { CP=P;       Q0=L; Q7=H; Bus=LHHHHHHH; }            // Vec 8
  Ann {* Shift 1R *}
  V { CP=P; D0=1; Q0=H; Q7=H; Bus=HLHHHHHH; }            // Vec 9
  Ann {* Shift 0R *}
  V { CP=P; D0=0; Q0=L; Q7=H; Bus=LHLHHHHH; }            // Vec 10
  Ann {* Shift 1R *}
  V { CP=P; D0=1; Q0=H; Q7=H; Bus=HLHLHHHH; }            // Vec 11
  Ann {* Shift 0R *}
  V { CP=P; D0=0; Q0=L; Q7=H; Bus=LHLHLHHH; }            // Vec 12
  Ann {* Shift 1R *}
  V { CP=P; D0=1; Q0=H; Q7=H; Bus=HLHLHLHH; }            // Vec 13
  Ann {* Shift 0R *}
  V { CP=P; D0=0; Q0=L; Q7=H; Bus=LHLHLHLH; }            // Vec -14
  Ann {* Shift 1R *}
  V { CP=P; D0=1; Q0=H; Q7=L; Bus=HLHLHLHL; }            // Vec 15

}

"""




"""
General syntax for STIL blocks: \s*(?P<name>[a-zA-Z]+)\s*{...}
    - Note, sections in STIL are partitioned via curly braces. 




6. STIL Syntax description: 
    This clause describes, in general, the basic syntax and semantic
    constructs of STIL. 

6.1 Case sensitivity
    SITL is case-sensitive; all tokens, including identifiers, are 
    manipulated in a case-sensitive fashion. For instance, "Dbus" and 
    "dbus" are two identifiers. 

6.2 Whitespace
    Whitespace in STIL is one or more of the following: 
            space
        \t  tab
        \n  newline character

6.3 Reserved words 
    All keywords are reserved for the explicit use as defined for the 
    keyword. STIL keywords have the first character of each word in
    upper case, and no underscores or spaces are used. For instance, 
    WaveformTable is a reserved word in STIL. 

    Reserved words are generally the first token in a STIL statement.
    They are used only in the context of that word, except for single-
    character reserved words, which may also appear in WaveformChar
    contexts. 

6.4 Reserved characters

6.5 Comments 
    There are two styles of comments in STIL: 
        //line comment     line coments are terminated by newline.
        /*block comment*/  block comments may span multiple lines.

    Comments may appear at any legal whitespace location and are 
    treated as whitespace. Nested block comments shall not be allowed
    (e.g., "/* /* */ */"), but line comments may be contained in 
    blocks statements. Comments defined using these constructs may not
    be preserved through STIL processes. See Clause 13 for annotations,
    which are a type of comment that is preserved through processes. 

    TODO: Need to check for nested blocks and error if found.

6.6 Token length: 
    Tokens are defined to be the block of text between reserved 
    characters, or reserved charactes themselves (other than whitespace
    and comment delimiters). Tokens are limited to maximum length of 
    1024 characters. Longer sequences of charater strings may be defined 
    by segementing the character strins into sections and placing a period
    between the sections (see 6.7).

6.7 Character Strings
    Blocks of text containing reserved characters or STIL-defined reserved
    words may be passed through STIL by double quoting the text. Signal 
    names that contains reserved characters or match STIL-defined reserved
    words, and text strings that contain whitespace, are maintained in a
    STIL file by enclosing the text in double qoutes. 

    .... 

6.8 User-defined name characteristics
    ...
    ...
    ...

    whitespace_chacter ::= " " | "\t" | "\n"

6.9 ...


7.0 Statement structure and organization of STIL information
    There are two general forms of STIL statements: simple and block 
    statements. Both forms start with a STIL keyword, followed by a 
    number of tokens (depending on the statement). The simple 
    statement is terminated by a semicolor. The block statement contains
    open and close braces; addtional STIL statements may occur inside
    these braces. The statement form are presented in Figure 30. 

    Simple statement: 
        Keyword (OPTIONAL_TOKENS)*;
    Block Statement: 
        Keyword (OPTIONAL_TOKENS)* {(OPTIONAL_MORE_STATEMENTS)*}

                Figure 30 - STIL statement structure.

7.1 STIL follows a "define before use" paradigm, with several expections
    discussed below. For example, the timing data is defined before it may 
    be references, and a name used to reference a group of signals 
    defines what signals it contains before it is used. Since all data is 
    defined inside "top-level" blocks, these requirements are satified by 
    properly ordering these top-level blocks.

    "Top-level" blocks that occur outside the context of any other STIL 
    statement. The first columns of Table 7 and Table 8 list all possible
    "top-level" blocks and statements in STIL.  

    Table - 7 STIL top-level statments and ordering requirements

    Statement     |               Purpose

    STIL: Defines the version of STIL present in the file. This is the 
          first statment of any STIL file, including files opened from 
          the Include statement



"""