import sys, os, re 
import KeyLookUps as KLU
import SymbolTable as STBL 

def lex(string='', file='', debug=False): 
    '''
    This function takes in either a string of file path and returns 
    a list of tokens. The tokens are, of course, based on the STIL 
    standard. 
    '''
    func = "lex"
    
    states = { "free" : True, 
               "string-literal" : False,
               "inline-comment" : False,
               "block-comment"  : False, 
               "ann"  : False,
               # -----------------------
               "toplevelblock" : False,
             }
    
    def classify_token(token): 
        if token in KLU.TopLevel.keywords: return token
        if token in KLU.Other.keywords: return token
        if KLU.References.re_digits.search(token): return 'digits'
        return 'identifier'

    
    # ---------------------------------------------:
    # Check inputs: 
    # ---------------------------------------------: 
    if not file and not string: 
        raise ValueError("Must provide either a string OR file reference.")
    if string and file: 
        raise ValueError("Cannot provide both a string and file reference.")
    if string: test = string 
    elif file: 
        if not os.path.isfile(file): raise ValueError("File is not valid: %s"%(file))
        f = open(file,'r'); test = f.read(); f.close()
        
    lineCount = 1; charOnLineIndex = 1
    lastchar = ''; nextchar = ''; inputLength = len(test) - 1; 
    tokens = []; token = []

    for i,char in enumerate(test):
        if debug: print("DEBUG: [%s]: %s"%(i,char))
        
        # Infastructure for lookahead: 
        if i == inputLength: nextchar = ''
        else: nextchar = test[i+1]
        # Infastructure for reporting: 
        if char == '\n': 
            lineCount += 1
            charOnLineIndex = 1
        else: charOnLineIndex += 1
        
        # TODO: This kinda stuff can go into the symbol table is needed. 
        # --------------------------------------------------------------: 
        # State section
        # --------------------------------------------------------------: 
        # String-literal state
        if states["string-literal"]: 
            if char == '\"' and lastchar != '\\': 
                if debug: print('DEBUG:  - closing string-literal state')
                states['string-literal'] = False; states['free'] = True
                token.append(char) # NOTE: We are keeping the double quotes. 
                _token = "".join(token)
                if _token:
                    tokens.append({'token':_token, 'tag':'identifier'})
                    token = []
            else: token.append(char)
            lastchar = char; continue; 
        # inline comment: 
        if states["inline-comment"]: 
            if char == '\n': 
                if debug: print('DEBUG:  - closing inline-comment state')
                states['inline-comment'] = False; states['free'] = True
            else: lastchar = char; continue;
        # block comment: 
        if states["block-comment"]: 
            if char == '/' and lastchar == '*': 
                if debug: print('DEBUG:  - closing block-comment state')
                states['block-comment'] = False; states['free'] = True
            else: lastchar = char; continue;
        # Ann comment: 
        if states["ann"]: 
            if char == '}' and lastchar == '*': 
                if debug: print('DEBUG:  - closing ann state')          
                _token = "".join(token)
                if _token:
                    #tag = classify_token(_token)
                    tokens.append({'token':_token, 'tag':'identifier'})
                    token = []
                tokens.append({'token':'*}', 'tag':'*}'})
                states['ann'] = False; states['free'] = True
            else: 
                token.append(char)
            lastchar = char; continue;
        # <other-states>
        # . . .
        # --------------------------------------------------------------: 
        # Freelance section 
        # --------------------------------------------------------------: 
        if char == '\"':  # Catch string-literals...
            if debug: print('DEBUG: (%s): - setting string-literal state'%(func))
            states['string-literal'] = True; states['free'] = False
            token.append(char) # NOTE: We are keeping the double quotes. 
            lastchar = char; continue; 
        if char == '/' and lastchar == '/':  # Catch inilne comments
            if debug: print('DEBUG: (%s)  - setting inline-comment state'%(func))
            states['inline-comment'] = True; states['free'] = False
            lastchar = char; continue;
        if char == '*' and lastchar == '/': # Catch block comments
            if debug: print('DEBUG: (%s):  - setting block-comment state'%(func))
            states['block-comment'] = True; states['free'] = False
            lastchar = char; continue;
        if char == '*' and lastchar == '{': # Catch annotations
            if debug: print('DEBUG: (%s):  - setting ann state'%(func))
            states['ann'] = True; states['free'] = False
            _token = "".join(token)
            if _token:
                if _token != 'Ann': 
                    raise RuntimeError("Should be 'Ann', found: %s"%(_token))
                tag = classify_token(_token)
                tokens.append({'token':_token, 'tag':tag})
                token = []
            tokens.append({'token':'{*', 'tag':'{*'})           
            lastchar = char; continue;
        
        # Storing Chars section: 
        if char in KLU.References.spaces: 
            if lastchar in KLU.References.spaces: # chained spaces
                lastchar = char; continue; 
            if token:
                if debug: print("DEBUG: - pushing token on space, %s"%("".join(token)))     
                _token = "".join(token)
                if _token:
                    tag = classify_token(_token)
                    tokens.append({'token':_token, 'tag':tag})
                    token = []
            else: lastchar = char; continue;
        
        elif char == "{": 
            if nextchar == "*": 
                lastchar = char; continue;
            _token = "".join(token)
            if _token:
                tag = classify_token(_token)
                tokens.append({'token':_token, 'tag':tag})
                token = []
            tokens.append({'token':char, 'tag':char})
        
        elif char in KLU.References.special:    
            _token = "".join(token)
            if _token:
                tag = classify_token(_token)
                tokens.append({'token':_token, 'tag':tag})
                token = []
            tokens.append({'token':char, 'tag':char})     
        elif char in KLU.References.alphanumeric: 
            token.append(char)        
        elif char == "/":
            token.append(char) 
        else: 
            if debug: print("DEBUG: Not sure what to do with char: %s"%(char))
        lastchar = char 
        
    # TODO: There is a current issue with the following: 
    # Signals {
    #  A[0..7] InOut: 
    # }
    # Technically 'A' is a reserved key word and '[' is a special character. 
    # However, in this context, 'A[0]' or 'A[0..7]' is the identifier. Thus, 
    # the lexer should look ahead, AT all instances of keywords found:( 
    # 
    # Section: 6.4 Reserved characters: 
    # ---------------------------------
    # '[]' Left and right square brackets are used to denote numeric indexes.
    # '""' Double quote character is used to denote literal strings.
    # 

    # reduce the tokens here: 
    finalTokens = []
    i = 0; done = len(tokens)
    while i < done:
        if tokens[i]['token'] == '[': 
            j = None; end = None; tmp = []
            try: 
                if tokens[i+5]['token'] == ']': 
                    end = i + 5
                j = i - 1
            except: pass 
            try: 
                if tokens[i+2]['token'] == ']': 
                    end = i + 2
                    j = i - 1
            except: pass 
            if j == None or end == None: 
                raise RuntimeError("Could located needed ']'")
            while j <= end:
                tmp.append(tokens[j]['token'])
                j+=1
            last = finalTokens.pop()
            finalTokens.append({'token':"".join(tmp),'tag':'identifier'})
            i = j 
        finalTokens.append(tokens[i])    
        i += 1 

    if debug: 
        print("DEBUG: Dumping new tokens")       
        for i, token in enumerate(finalTokens,start=0): 
            print(i, token)
    
    #return tokens 
    return finalTokens 


def tpl_tagger(tplp, fileKey='', string = '', file = '', debug = False):
    func = "STILutils.__tpl_tagger" 

    states = { "free" : True, 
               "string-literal" : False,
               "inline-comment" : False,
               "block-comment"  : False, 
               "ann"  : False,
               # -----------------------
               "top-level-element" : False,
             }

    # Check intpu First check the current layout of tplp
    if not fileKey: raise ValueError("need to provide filekey")
    if fileKey in tplp: raise RuntimeError("Contain double instances of: ", fileKey)
    else:  tplp[fileKey] = {}
        
    # Load STIL-string: 
    if string: test = string
    else: f = open(file,'r'); test = f.read(); f.close()
    

    # Hooks for handling reporting.
    lineCount = 1; charOnLineIndex = 1

    lastchar = ''; nextchar = ''; inputLength = len(test)-1;

    block = ''
    cbs = 0
    token  = [] 
    stack = [] # Should only be of Toplevel Keywords and never more than one character.
    
    UserKeywords = []
    UserFunctions = []

    for i,char in enumerate(test, start = 0):  
        if debug: print("DEBUG: [%s] %s"%(i,char))

        # Infastructure for lookahead: 
        if i == inputLength: nextchar = ''
        else: nextchar = test[i+1]
    
        # Infastructure for reporting: 
        if char == '\n': 
            lineCount += 1
            charOnLineIndex = 1
        else: charOnLineIndex += 1
        # TODO: This kinda stuff can go into the symbol table is needed. 

        # --------------------------------------------------------------: 
        # State section
        # --------------------------------------------------------------: 
        # String-literal state
        if states["string-literal"]: 
            if char == '\"' and lastchar != '\\': 
                if debug: print('DEBUG:  - closing string-literal state')
                states['string-literal'] = False; states['free'] = True
            else: token.append(char)
            lastchar = char; continue; 
        # inline comment: 
        if states["inline-comment"]: 
            if char == '\n': 
                if debug: print('DEBUG:  - closing inline-comment state')
                states['inline-comment'] = False; states['free'] = True
            else: lastchar = char; continue;
        # block comment: 
        if states["block-comment"]: 
            if char == '/' and lastchar == '*': 
                if debug: print('DEBUG:  - closing block-comment state')
                states['block-comment'] = False; states['free'] = True
            else: lastchar = char; continue;
        # Ann comment: 
        if states["ann"]: 
            if char == '}' and lastchar == '*': 
                if debug: print('DEBUG:  - closing ann state')
                states['ann'] = False; states['free'] = True
                if stack[-1] == 'Ann': 
                    tplp[fileKey][stack.pop()][-1]['end'] = i 
                    block = ''; token = []
            else: 
                token.append(char)
            lastchar = char; continue;
        
        # NOTE: as long as this is placed last, that is behind the spaces
        if states["top-level-element"]: 
            if char == "{": 
                if nextchar == "*": lastchar = char; continue;
                cbs += 1
                lastchar = char; continue
                
            if char == "}": 
                cbs -= 1
                if cbs == 0: 
                    tplp[fileKey][stack.pop()][-1]['end'] = i
                    stack = []; token = []
                    states["top-level-element"] = False 
                    states["free"] = True
                lastchar = char; continue
                
            if char == ';': 
                if cbs == 0: 
                    entity = stack.pop()
                    if entity == "UserKeywords": 
                        _start = tplp[fileKey][entity][-1]['start']
                        tmp = string[_start:i]
                        r = re.compile('\w+')
                        match = r.findall(tmp)
                        for m in match[1:]:
                            if m in UserKeywords: pass
                            else: UserKeywords.append(m) 
                        tplp[fileKey][entity][-1]['keys'] = match[1:]
                    elif entity == "UserFunctions": 
                        _start = tplp[fileKey][entity][-1]['start']
                        tmp = string[_start:i]
                        r = re.compile('\w+')
                        match = r.findall(tmp)
                        for m in match[1:]:
                            if m in UserFunctions: pass
                            else: UserFunctions.append(m) 
                        tplp[fileKey][entity][-1]['keys'] = match[1:]
                    tplp[fileKey][entity][-1]['end'] = i
                    stack = []; token = []
                    states["top-level-element"] = False 
                    states["free"] = True
                lastchar = char; continue
            #lastchar = char; continue
            
            # No you cant skip becasue you need to be able to catch interal strings 

        # This is actually a little di
            
        # <other-states>
        # . . . 
        
        # --------------------------------------------------------------: 
        # Freelance section 
        # --------------------------------------------------------------: 
        if char == '\"':  # Catch string-literals...
            if debug: print('DEBUG  - setting string-literal state') 
            states['string-literal'] = True; states['free'] = False
            lastchar = char; continue; 
        if char == '/' and nextchar == '/':  # Catch inilne comments
            if debug: print('DEBUG:  - setting inline-comment state')
            states['inline-comment'] = True; states['free'] = False
            lastchar = char; continue;
        if char == '*' and lastchar == '/': # Catch block comments
            if debug: print('DEBUG:  - setting block-comment state')
            states['block-comment'] = True; states['free'] = False
            lastchar = char; continue;
        if char == '*' and lastchar == '{': # Catch annotations
            if debug: print('DEBUG  - setting ann state')
            states['ann'] = True; states['free'] = False
            lastchar = char; continue;
            
        # Storing chars.....
        #  - If this is a consecutive space, jsut skip, tokens were already handled. 
        #  - If nothing in token-list, skip. 
        if char in KLU.References.spaces: 
            
            # Consecutive Spaces... skip 
            if lastchar in KLU.References.spaces: lastchar = char; continue; 
                
            # Nothing is stored in tokens... skip    
            if not token: lastchar = char; continue;
                
            _token = "".join(token); token = []
            if debug: print("DEBUG: - pushing token on space, %s"%(_token))
                
            if stack: lastchar = char; continue 
            # ^ If the stack is present we continue, because we only will 
            # shut down on a ';' or closing '}'.
            # This is bascially a state-dependent check, thus we may be able to 
            # to remove this if we handle this in the States-Section. 

            if ( (_token not in KLU.TopLevel.keywords) and (_token not in UserKeywords) and (_token not in UserFunctions)):
                    raise RuntimeError("Not sure: token: %s, stack :%s"%(_token, stack))
            else: 
                # If we maintain the stack is only ONE or NONE element, then 
                # we can check state simply by checking the len of stack rather
                # then checking the elements. 
                stack.append(_token)
                states['top-level-element'] = True
                states['free'] = False                                 
                #print(block, len(block), _token)
                if stack[-1] in tplp[fileKey]: 
                    tplp[fileKey][_token].append({'start': i-len(_token),'end':-1} )
                else: tplp[fileKey][_token] = [{'start':i-len(_token),'end':-1}]                                   

                if debug: 
                    print(tplp)
                lastchar = char; continue  
        
        elif char == "{": 
            if nextchar == "*": lastchar = char; continue;
            else: # sh
                cbs += 1
                            
                if not token: lastchar = char; continue; 
                            
                _token = "".join(token); token = []            
                if debug: print("DEBUG: - pushing token on space, %s"%(_token))
                    
                if stack: lastchar = char; continue 
                                
                #print(block, len(block), _token)
                if _token not in KLU.TopLevel.keywords: raise RuntimeError("Not sure: token: %s, stack :%s"%(_token, stack))

                else: # Here
                    # If we maintain the stack is only ONE or NONE element, then 
                    # we can check state simply by checking the len of stack rather
                    # then checking the elements. 
                    stack.append(_token)
                    states['top-level-element'] = True
                    states['free'] = False                         
                    #print(block, len(block), _token)
                    if stack[-1] in tplp[fileKey]: 
                        tplp[fileKey][_token].append( {'start': i-len(_token),'end':-1} )
                    else: tplp[fileKey][_token] = [{'start':i-len(_token),'end':-1}]                                   
                    lastchar = char; continue  

        else: # IF char NOT a space OR '{' (remmber, all other cases should be handled by the state machine). 
            token.append(char)
        #elif char in References.alphanumeric: 
        #    token.append(char)
        #else: 
        #    if debug: print("DEBUG:  - Not sure what to do with char: %s"%(char))
                
                
        # NOTE: At this point, I believe we should be storing no matter what, rather than 
        # checking is the char in an alphanumeric.....
        lastchar = char      


    #if UserKeywords: 
    #    print(tplp[fileKey]["UserKeywords"])
    #    tplp[fileKey]["UserKeywords"]["keys"] = UserKeywords
    #if UserFunctions: 
    #    tplp[fileKey]["UserKeywords"]["keys"] = UserFunctions
    return tplp


def tplp_check_and_object_builder(tplp, fileKey, string, debug = False):
    """
    TODO: This is where the config file may take large effect. For example,
    we do not parse the Signals or SignalGroups block becasue they can be
    large and complicated. However, if the users wants we can parse all that
    because they know they will want it. 


    The main jobs of this method is too: 
      (1) return dictionay of TOP level blocks 
      (2) Each STIL block contains a list of individual dictionary where 
          each one is holding relevant content specific to each block
       (3) Typical information is domain-names and start and end char-indexes.
           however, each block is subject to its own defintion of what it should
           store. 
    STIL: 
        CHECKS: 
          1.) Check that it is first. 

        OBJECT: None
          It is only a number - easy to extrat from symboltable.
    
    Header: 
        CHECKS: 
          1.) If present, make sure it is second. 
    
        OBJECT: None 
    
    Include: 
        CHECKS: None 
          Only if the Include exits, then the object builder will check syntax.
        
        OBJECT: {'file':<include-path>, 'IfNeed': None | [list-of-TopLevel-Elements] }
           NOTE: Doesnt not check paths here. (SUBJECT OT CHANGE)
      
    Signals: 
        CHECKS:
          1.) If many instances, only first one is kept.

        OBJECT: None 
    
    SignalGroups: 
        CHECKS: 
          1.) If present, domain names are checked. 

        OBJECT: List of dictionaries. 
          ex.) [{'name':<domain-name>, 'start': <start-index>, 'end': <end-index>] 

    PatternExec: 
        CHECKS: 
          1.) Checks domain names.  

        OBJECT: List of dictionaries. 
          ex.) {'name': execName, 'start':indexes['start'], 'end':indexes['end'],
                'Category':category, 'Selector':selector, 'Timing':timing,
                'DCLevels':dclevels, 'DCSets': dcsets, 'PatternBurst':patternburst})

    PatternBurst: 
        CHECKS: TODO

        OBJECT: List of dictionaries 
          ex.) TODO

    Pattern: 
        CHECKS: TODO

        OBJECT: TODO 
          ex.) TODO

    Timing: 
        CHECKS: TODO

        OBJECT: TODO

            
      
    """
    func = "STIL.__tplp_check_and_object_builder"
    if debug: print("DEBUG: (%s): Starting sanity checks"%(func))
    objectMap = {}
    # Error out if you find mistake
    # builder necessary objects and return object holder: 
    
    # TODO: SANITY CHECKS!
    # 8.0 STIL Statement: 
    # -------------------
    # 'The STIL statement shalle be the first statement of the STIL file.'
    if next(iter(tplp[fileKey])) != 'STIL': 
        raise RuntimeError("First block must be 'STIL'.")

    # 9.0 Header Block
    # ----------------
    # 'Contains general information about the STIL file being parsed.'
    # 'This block is optional; if present, it shall be the first statement
    # after the STIL statement for a file.'
    # 'The Header block may appear only once at the beginning of a STIL file. '
    if 'Header' in tplp[fileKey]: 
        if len(tplp[fileKey]["Header"]) != 1: 
            raise RuntimeError("The Header block may appear only once in the STIL.")
    
        if list(tplp[fileKey].keys())[1] != 'Header': 
            raise RuntimeError("The Header block, if present, must come directly after the STIL statement.")
    
        if debug: print("DEBUG:   - Header passed.")   
            
    # 10.0 Include statement: 
    # -----------------------
    # The include statement may occur at any point at which a legal STIL 
    # statement may be defined. 
    #
    
    # TODO: Where should we be storing the regex? This goes for any block..
    # When do we check the file path of the include statements? We should 
    # have a flag  (through a config setup) that checks whether we checks 
    # the  include files at all. 
    # 
    if 'Include' in tplp[fileKey]: 
        objectMap['Include'] = []
        RE_Include_only   = re.compile("Include")
        RE_Include_file   = re.compile("Include\s+\"(?P<file>.+)\"\s*;")
        RE_Include_IfNeed = re.compile("Include\s+\"(?P<file>.+)\"\s+IfNeed\s+(?P<blocks>[\w\s\,]+);")
        
        # Need to extract the full expression
        # Store the Includes in list 
        for indexes in tplp[fileKey]['Include']: 
            tmp = string[indexes['start']:indexes['end'] + 1]
            #print(tmp)
            match = RE_Include_file.search(tmp)
            if match: 
                objectMap['Include'].append({'file':match.group('file'),'IfNeed': None})
                continue 
            match = RE_Include_IfNeed.search(tmp)
            if match: 
                blocks = [block.strip(' ') for block in match.group('blocks').split(',')]
                for block in blocks: 
                    if block not in KLU.TopLevel.keywords: 
                        raise ValueError("Include contains a non top-level keyword: %s"%(block))
                objectMap['Include'].append({'file':match.group('file'),'IfNeed': blocks})
        if debug:print("DEBUG:   - Includes passed: %s"%(objectMap['Include']))
            
    # 14. Signals Block: 
    # Only one Signals block is allowed in a STIL file set; any other Signal block parsed 
    # is ignored. This is to facilitate the collection of several separate STIL programs
    # for a DUT into a complete test. 
    # 
    # TODO: Does this mean, that the first one is the one to be used and all others 
    # will simply be ignored - that is to say, they will be skipped but NOT throw
    # an error? 
    if 'Signals' in tplp[fileKey]: 
        if (len(tplp[fileKey]['Signals']) > 1): 
            print("TODO: Many Signal blocks found, delete all references but the first one ")
        if debug: print("DEBUG:   - Signals passed.")
    else: 
        if debug:print("DEBUG:   - No Signals present. ")
            
    # 15. SignalGroups block: 
    # -----------------------
    # Only one global SignalGroups blocks shall be allowed in STIL. A global SignalGroups
    # block is a SignalGroups block with no DOMAIN_NAME specified. 
    # 
    # Any number of SignalGroups blocks with domain_names are allowed. ALl
    # domain_names shall be unique across all SignalGroups (A name in one domain may be
    # the same as a name in another domain without conflicting. See 6.16 for details on 
    # name conflict resolution).
    #
    # TODO: A fair question here is to determine if we should call on the lexer and symbol table? 
    # although, it would certainly work, I believe it would be overkill for now. Even though, 
    # we are reading in the entire block, we still dont need to lex/symtbl it. A further point, 
    # would be that we dont want to do that his because there might be many defined SignalGroups
    # but only one is atually reference via the patterns or patternexec. Also, we should 
    # really wait until the user asks for it. 
    # 
    # TODO: Does STIL set any domain-name size limitations? probably not, That would typically 
    # be on the end machine. STIL wouldnt want to set such a limit because perhaps a tester
    # had a higher limit.
    
    if 'SignalGroups' in tplp[fileKey]:
        objectMap['SignalGroups'] = []
        if debug: print("\nSanity Checking SignalGroups blocks...")
        singleGlobal = False
        RE_SignalGroups_global = re.compile("^SignalGroups\s*\{")
        RE_SignalGroups_DomainName_no_dqoutes   = re.compile("^SignalGroups\s+(?P<name>\w+)\s*\{")
        RE_SignalGroups_DomainName_with_dqoutes = re.compile("^SignalGroups\s+(?P<name>\".*\")\s*\{")
        
        for indexes in tplp[fileKey]['SignalGroups']: 
            tmp = string[indexes['start']:indexes['end'] + 1]
            #print(tmp)
            
            # Match for global: 
            match = RE_SignalGroups_global.search(tmp)
            if match: 
                if singleGlobal: 
                    raise RuntimeError("Found more than one global SignalGroups.")
                else: 
                    singleGlobal = True
                    #objectMap['SignalGroups'].append(References.GLOBAL) # should it store the locations?
                    objectMap['SignalGroups'].append({'name'  : KLU.References.GLOBAL, 
                                                      'start' : indexes['start'], 
                                                      'end'   : indexes['end']})
                    continue 
            # Match for NO double qoutes:      
            match = RE_SignalGroups_DomainName_no_dqoutes.search(tmp)
            if match: 
                domain = match.group('name')
                if domain in objectMap['SignalGroups']: 
                    raise RuntimeError("All SignalGroups domain names must be unique; 2 instances of %s"%(domain))
                #objectMap['SignalGroups'].append(domain)
                objectMap['SignalGroups'].append({'name': domain, 'start':indexes['start'], 'end':indexes['end']})
                continue 
            # Match for double qoutes:      
            match = RE_SignalGroups_DomainName_with_dqoutes.search(tmp)
            if match: 
                domain = match.group('name')
                if domain in objectMap['SignalGroups']: 
                    raise RuntimeError("All SignalGroups domain names must be unique; 2 instances of %s"%(domain))
                #objectMap['SignalGroups'].append(domain)
                objectMap['SignalGroups'].append({'name': domain, 'start':indexes['start'], 'end':indexes['end']})
                
                continue 
                    
        # TODO: As we performt these simple checkc, we should be caching some of this basic information. 
        if debug: 
            print("DEBUG: SignalGroups passed.")
            for domain in objectMap['SignalGroups']: 
                print("DEBUG:  -  %s"%(domain))
                
    # 15. PatternExec block: 
    # ----------------------
    # "Only one global PatternExec block shall be allowed in STIL. A global
    # PatternEec block is a PatternExec block with no domain name speficied. 
    # - Any number of PatternExec blocks with domain_names are allowed. All 
    # domain names shall be unique across all PatternExec blocks."
    # 
    # TODO: What happens with translation tools where mutiple PatternExec
    # blocks are defined? It seems that STIL has no issue with it. Would somethign
    # like STILReader create multiple outputs? 
    # 
    if 'PatternExec' in tplp[fileKey]:
        objectMap['PatternExec'] = []
        print("\nSanity Checking PatternExec blocks...")
        singleGlobal = False
        
        RE_PatternExec_global = re.compile("^PatternExec\s*\{")
        RE_PatternExec_DomainName_no_dqoutes = re.compile("^PatternExec\s+(?P<name>\w+)\s*\{")
        RE_PatternExec_DomainName_with_dqoutes = re.compile("^PatternExec\s+(?P<name>\".*\")\s*\{")
        
        # Category 
        # TODO: Can you have multiple Category instances? 
        RE_Category = re.compile("Category(?P<name>.*);")
        RE_Selector = re.compile("Selector(?P<name>.*);")
        RE_Timing = re.compile("Timing(?P<name>.*);")
        RE_DCLevels = re.compile("DCLevels(?P<name>.*);")
        RE_DCSets = re.compile("DCSets(?P<name>.*);")
        RE_PatternBurst = re.compile("PatternBurst(?P<name>.*);")
        
        execName = None; category = None; selector = None; 
        timing = None; dclevels = None; dcsets = None; patternburst = None; 
        
        for indexes in tplp[fileKey]['PatternExec']: 
            execName = None; category = None; selector = None; 
            timing = None; dclevels = None; dcsets = None; patternburst = None; 
            tmp = string[indexes['start']:indexes['end'] + 1]
            # Match for global:
            match = RE_PatternExec_global.search(tmp)       
            if match:
                if singleGlobal: 
                    raise RuntimeError("Found more than one global SignalGroups.")
                else:
                    singleGlobal = True
                    execName = KLU.References.GLOBAL
            match = RE_PatternExec_DomainName_no_dqoutes.search(tmp)       
            if match: execName = match.group("name")
            match = RE_PatternExec_DomainName_with_dqoutes.search(tmp)       
            if match: execName = match.group("name")
            
            if not execName: raise RuntimeError("Couldnt extract PatternExec name.")
                
            match = RE_Category.search(tmp)
            if match: category = match.group("name").strip()

            match = RE_Selector.search(tmp)
            if match: selector = match.group("name").strip()
                
            match = RE_Timing.search(tmp)
            if match: timing = match.group("name").strip()
                
            match = RE_DCLevels.search(tmp)
            if match: dclevels = match.group("name").strip()
                
            match = RE_DCSets.search(tmp)
            if match: dcsets = match.group("name").strip()    
        
            match = RE_PatternBurst.search(tmp)
            if match: patternburst = match.group("name").strip() 
            #else: raise RuntimeError("PatternExec must contain a PatternBurst block.")
            # NOTE: Cant error is PatBrst is not present, 'The statement may not be present
            # for contexts that are passing Timing information only.'
        
            # LAst thing, add the 
            objectMap['PatternExec'].append({'name': execName, 
                                              'start':indexes['start'], 
                                              'end':indexes['end'],
                                              'Category':category,
                                              'Selector':selector,
                                              'Timing':timing,
                                              'DCLevels':dclevels,
                                              'DCSets': dcsets,
                                              'PatternBurst':patternburst})
    # 17 PatternBurst block: 
    # ----------------------
    # Because the PatternBurst is relatively small, but highly variable in its structure,
    # We can tyr using the lexer + symbol table to build the dictionary, rather than 
    # using a complicated structure of regexes. 
    # 
    if 'PatternBurst' in tplp[fileKey]:
        objectMap['PatternBurst'] = []
        print("\nSanity Checking PatternBurst blocks...")
        singleGlobal = False
        
        RE_PatternBurst_DomainName_no_dqoutes = re.compile("^PatternExec\s+(?P<name>\w+)\s*\{")
        RE_PatternBurst_DomainName_with_dqoutes = re.compile("^PatternExec\s+(?P<name>\".*\")\s*\{")
        
        RE_SignalGroups = re.compile("SignalGroups(?P<name>.*);")
        RE_MacroDefs = re.compile("MacroDefs(?P<name>.*);")
        RE_Procedures = re.compile("Procedures(?P<name>.*);")
        RE_ScanStructures = re.compile("ScanStructures(?P<name>.*);")
        RE_Start = re.compile("Start(?P<name>.*);")
        RE_Stop = re.compile("Stop(?P<name>.*);")
        

        for indexes in tplp[fileKey]['PatternBurst']: 
            tmp = string[indexes['start']:indexes['end'] + 1]
            tokens = lex(string=tmp, debug=debug)
            symtbl = STBL.SymbolTable(tokens, debug = debug)
            print(symtbl)
            pbd = patternburst_map_maker(tokens, symtbl, debug)
            print(pbd)
            print("TODO: Convert this object to the objectmap here ")
            
            objectMap['PatternBurst'].append({ 'start':indexes['start'], 
                                              'end':indexes['end'],} )  
            objectMap['PatternBurst'][-1].update(pbd)
    
    
        if debug: print("DEBUG: (%s): Done..."%(func))


    # 23. Pattern Block: 
    # ------------------
    # "The Pattern block shall have a domain name. The name-space of the Pattern
    # is shared with the PatternBurst names. The set of names across both 
    # PatternBurst and Pattern blocks shall be unique. "
    if 'Pattern' in tplp[fileKey]:
        objectMap['Pattern'] = []
        print("\nSanity Checking Pattern blocks...")


        RE_Pattern_DomainName_no_dqoutes = re.compile("^Pattern\s+(?P<name>\w+)\s*\{")
        RE_Pattern_DomainName_with_dqoutes = re.compile("^Pattern\s+(?P<name>\".*\")\s*\{")
        
        for indexes in tplp[fileKey]['Pattern']: 
            tmp = string[indexes['start']:indexes['end'] + 1]
            match = RE_Pattern_DomainName_no_dqoutes.search(tmp)
            if match: 
                name = match.group("name")
                objectMap['Pattern'].append({'name': name,  
                                             'start':indexes['start'], 
                                              'end':indexes['end'],} )  
                continue 
            match = RE_Pattern_DomainName_with_dqoutes.search(tmp)
            if match: 
                name = match.group("name")
                objectMap['Pattern'].append({'name': name,  
                                             'start':indexes['start'], 
                                              'end':indexes['end'],} )  
                continue 
            raise RuntimeError("Found not Pattern name.")

    # TODO: Other toplevel checks

    # 18 Timing Block: 
    # ----------------
    # "Timing domain names: optional. If no name is present, then the timing
    # defined in this block is applied to any block without references to n
    # named timing."
    #
    if 'Timing' in tplp[fileKey]:
        objectMap['Timing'] = []
        if debug: print("\nSanity Checking Timing blocks...")
        
        RE_Timing_global = re.compile("^Timing\s*\{")
        RE_Timing_DomainName_no_dqoutes = re.compile("^Timing\s+(?P<name>\w+)\s*\{")
        RE_Timing_DomainName_with_dqoutes = re.compile("^Timing\s+(?P<name>\".*\")\s*\{")
        domainNames = [RE_Timing_global, RE_Timing_DomainName_no_dqoutes, RE_Timing_DomainName_with_dqoutes]
        singleGlobal = False
        _foundNames = []

        for indexes in tplp[fileKey]['Timing']: 
            timingBlockName = ""
            tmp = string[indexes['start']:indexes['end'] + 1]
            # Grab timing block name. 
            i = 0; iend = len(domainNames) - 1
            while i <= iend:
                match = domainNames[i].search(tmp)
                if match: 
                    if i == 0: # Global name
                        if singleGlobal: raise RuntimeError("Found second global timing block")
                        singleGlobal = True
                        timingBlockName = KLU.References.GLOBAL
                        if timingBlockName in _foundNames: 
                            raise RuntimeError("Found two timing blocks of the same name")
                        break 
                    elif i >= 1: 
                        timingBlockName = match.group("name")
                        if timingBlockName in _foundNames: 
                            raise RuntimeError("Found two timing blocks of the same name")
                        break
                i += 1
            # Other checks 
            # NOTE: At this point, it is a design question if we wish to 
            # dig deeper. That is, if we wish to mark all the start and stop 
            # chars of the WaveformTable, SubWaveforms, and Waveforms.
            # For now, I will leave that to the query.  
            objectMap['Timing'].append({'name': timingBlockName,
                                             'start':indexes['start'], 
                                              'end':indexes['end'],} )
    # 19. Spec Blocks: 
    # ----------------
    # Spec blocks are used to define the value of the variables and expressions
    # that are used within the waveform definitions. Each Spec block may contain
    # Catergory blocks (which contain spec variable defintions), or Variable 
    # defintions directly. 
    if 'Spec' in tplp[fileKey]:
        objectMap['Spec'] = []
        if debug: print("\nSanity Checking Spec blocks...")
        RE_Spec_DomainName_no_dqoutes = re.compile("^Spec\s+(?P<name>\w+)\s*\{")
        RE_Spec_DomainName_with_dqoutes = re.compile("^Spec\s+(?P<name>\".*\")\s*\{")
        
        for indexes in tplp[fileKey]['Spec']: 
            tmp = string[indexes['start']:indexes['end'] + 1]
            match = RE_Spec_DomainName_no_dqoutes.search(tmp)
            if match: 
                name = match.group("name")
                objectMap['Spec'].append({'name': name,  
                                          'start':indexes['start'], 
                                          'end':indexes['end'],} )  
                continue 
            match = RE_Spec_DomainName_with_dqoutes.search(tmp)
            if match: 
                name = match.group("name")
                objectMap['Spec'].append({'name': name,  
                                             'start':indexes['start'], 
                                              'end':indexes['end'],} )  
                continue 
            raise RuntimeError("Found no name for Spec.")
    if 'Selector' in tplp[fileKey]:
        objectMap['Selector'] = []
        if debug: print("\nSanity Checking Selector blocks...")
        RE_Selector_DomainName_no_dqoutes = re.compile("^Selector\s+(?P<name>\w+)\s*\{")
        RE_Selector_DomainName_with_dqoutes = re.compile("^Selector\s+(?P<name>\".*\")\s*\{")
        
        for indexes in tplp[fileKey]['Selector']: 
            tmp = string[indexes['start']:indexes['end'] + 1]
            match = RE_Selector_DomainName_no_dqoutes.search(tmp)
            if match: 
                name = match.group("name")
                objectMap['Selector'].append({'name': name,  
                                          'start':indexes['start'], 
                                          'end':indexes['end'],} )  
                continue 
            match = RE_Selector_DomainName_with_dqoutes.search(tmp)
            if match: 
                name = match.group("name")
                objectMap['Selector'].append({'name': name,  
                                             'start':indexes['start'], 
                                              'end':indexes['end'],} )  
                continue 
            raise RuntimeError("Found no name for Selector.")
        

    return objectMap

def patternburst_map_maker(tokens, symbolTable, debug = False): 
    """
    This class takes in a tokens an symboltable and will create a custom
    dictionary object holding all the necessary information. 
    """
    # NOTE: Honestly, I dont know if I need the symbol table for this? 
    # I can simply eat all the tokens and simply set state flags to control 
    # context information. 
    
    
    
    pb      = symbolTable.get_next_curly_set( symbolTable['PatternBurst'][0])
    patList = symbolTable.get_next_curly_set( symbolTable['PatList'][0])
    
    objectMap = {}
    # objectMap['SignalGroups'] = 
    # ...
    # objectMap['PatList'] = {
    #    {'pat' : <pat- or burst-name>, 
    #      IF 'SignalGroups': ..., }
    # }
    i = pb[0] + 1
    if tokens[1]['tag'] == 'identifier' and tokens[2]['tag'] == '{': 
        name = tokens[1]['token']
    elif tokens[1]['tag'] == '{': 
        name=  KLU.References.GLOBAL
    else: 
        raise RuntimeError("Recieved bad input: %s"%(tokens))
        
    objectMap['name'] = name 
    
    string = ''
    cbs = 0
    end = patList[0] - 1
    while i <= end: 
        

        if cbs == 0:
            # TODO: Really need to improve the error messaging. 
            if tokens[i]['tag'] == "SignalGroups": 
                if tokens[i+1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: objectMap['SignalGroups'] = tokens[i+1]['token']
                i += 3; continue
            if tokens[i]['tag'] == "MacroDefs": 
                if tokens[i+1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: objectMap['MacroDefs'] = tokens[i+1]['token']
                i += 3; continue
            if tokens[i]['tag'] == "Procedures": 
                if tokens[i+1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: objectMap['Procedures'] = tokens[i+1]['token']
                i += 3; continue
            if tokens[i]['tag'] == "ScanStructures": 
                if tokens[i+1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: objectMap['ScanStructures'] = tokens[i+1]['token']
                i += 3; continue
            if tokens[i]['tag'] == "Stop": 
                if tokens[i+1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: objectMap['Stop'] = tokens[i+1]['token']
                i += 3; continue
            if tokens[i]['tag'] == "Start": 
                if tokens[i+1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: objectMap['Start'] = tokens[i+1]['token']
                i += 3; continue
        # TODO: Handle Termination
                
        i += 1 # Last statement in loop. 


    
    i = patList[0] + 1; # The ' + 1' is because it starts on the 'curly'
    string = '' 
    pats = [] # NOTE: THis should be a list of dictionaries so that I can just set it in Objetmap 
    cbs = 0
    while i <= patList[-1] - 1: 
        print(tokens[i])
        if i == patList[0] + 1: # The first iteration: 
            if tokens[i]['tag'] != 'identifier': 
                raise RuntimeError("Received non 'identifier' tag", tokens[i]['tag'])
            #pats.append(tokens[i]['token'])
            pats.append({'name':tokens[i]['token']})
            i += 1; continue 

        if tokens[i]['tag'] == '{': # place holder for now
            cbs += 1
    
        if tokens[i]['tag'] == '}': # place holders for now
            cbs -= 1

        if cbs == 0 and tokens[i]['tag'] == 'identifier': 
            #pats.append(tokens[i]['token'])
            pats.append({'name':tokens[i]['token']})
            
        if cbs == 1: # In a PatList
            if tokens[i]['tag'] == "SignalGroups": 
                if tokens[i+1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: pats[-1]['SignalGroups'] = tokens[i+1]['token']
                i += 3; continue
            if tokens[i]['tag'] == "MacroDefs": 
                if tokens[i+1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: pats[-1]['MacroDefs'] = tokens[i+1]['token']
                i += 3; continue
            if tokens[i]['tag'] == "Procedures": 
                if pats[-1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: objectMap['Procedures'] = tokens[i+1]['token']
                i += 3; continue
            if tokens[i]['tag'] == "ScanStructures": 
                if tokens[i+1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: pats[-1]['ScanStructures'] = tokens[i+1]['token']
                i += 3; continue
            if tokens[i]['tag'] == "Stop": 
                if tokens[i+1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: pats[-1]['Stop'] = tokens[i+1]['token']
                i += 3; continue
            if tokens[i]['tag'] == "Start": 
                if tokens[i+1]['tag'] == ';': raise RuntimeError("Bad syntax. Expecting ';', ")
                else: pats[-1]['Start'] = tokens[i+1]['token']
                i += 3; continue
        # TODO: Handle Termination
        i += 1
    # Handling Patlist: TODO: Still need to handle all the other portions of the Patlist.
    if pats: 
        objectMap['PatList'] = {'pats': pats}
    return objectMap


def greetings():
    return "Greetings from PySTIL.utils"
