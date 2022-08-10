import os
import contextlib
import gzip
import re
import references
# ----------------------------------------------------------------------------:
def report_filesize_and_processing(start,end,ln,File,debug=False):
    func = "report_filesize_and_processing"
    filesize = os.path.getsize(File)
    if int(filesize) >= 100000: filesize = filesize / 1000000.0; unit = "MB"
    else: unit = "B"
    print("DEBUG: [%s]: Processing time : %s sec."%(func,end - start)) 
    print("DEBUG: [%s]: Lines processed : %s lines."%(func,ln))
    print("DEBUG: [%s]: File-size       : %s %s."%(func,filesize,unit))
# ----------------------------------------------------------------------------:
def get_domain_name(line,kw): 
    sline = line.split()
    if sline[0] != kw: 
        raise ValueError("Beginning of line doesn't match keyword provided: "\
                         "kw = %s, line = %s"%(kw, line))
    domain = str(references.GLOBAL_DOMAIN)
    if len(sline) > 1: 
        if sline[1] != "{": 
            domain = sline[1]
    return domain 
# ----------------------------------------------------------------------------:
def _read_line(File):
    if File.endswith(".gz"):
        with contextlib.closing(gzip.open(File,'r')) as fh: 
            for ln, line in enumerate(fh,start=1): 
                line = line.strip()
                if not line: continue 
                if line.startswith("//"): continue 
                yield ln, line
    else: 
        with open(File,"r") as fh: 
            for ln, line in enumerate(fh,start=1): 
                line = line.strip()
                if not line: continue 
                if line.startswith("//"): continue 
                yield ln, line
# ----------------------------------------------------------------------------:
def _read_line_range(File,start,end=0):
    i = 0
    if File.endswith(".gz"):
        with contextlib.closing(gzip.open(File,'r')) as fh: 
            for ln, line in enumerate(fh,start=1): 
                i += 1; 
                if i < start: continue 
                if i > end and end: break 
                line = line.strip()
                if not line: continue 
                if line.startswith("//"): continue 
                yield ln, line.strip()
    else: 
        with open(File,"r") as fh: 
            for ln, line in enumerate(fh,start=1): 
                i += 1; 
                if i < start: continue 
                if i > end and end: break 
                line = line.strip()
                if not line: continue 
                if line.startswith("//"): continue 
                yield ln, line
# ----------------------------------------------------------------------------:
def classify_token(token): 
    if token in references.TOP_LEVEL_KEYWORDS: return token
    if token in references.OTHER_KEYWORDS:     return token
    if references.re_digits.search(token):     return 'digits'
    return 'identifier'
# ----------------------------------------------------------------------------:
def lex(data,debug=False): 
    if isinstance(data,list): 
        data = " ".join(data)

    states = { "free" : True, 
               "string-literal" : False,
               "inline-comment" : False,
               "block-comment"  : False, 
               "ann"  : False,
             }
    lineCount = 1; charOnLineIndex = 1
    lastchar = ''; nextchar = ''; inputLength = len(data) - 1; 
    tokens = []; token = []

    for i, char in enumerate(data): 
        if debug: print("DEBUG: [%s]: %s"%(i,char))
        
        # Infastructure for lookahead: 
        if i == inputLength: nextchar = ''
        else: nextchar = data[i+1]
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
        if char in references.spaces: 
            if lastchar in references.spaces: # chained spaces
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
        
        elif char in references.special:    
            _token = "".join(token)
            if _token:
                tag = classify_token(_token)
                tokens.append({'token':_token, 'tag':tag})
                token = []
            tokens.append({'token':char, 'tag':char})     
        elif char in references.alphanumeric: 
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

