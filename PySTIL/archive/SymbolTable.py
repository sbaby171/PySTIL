'''
This module holds the implementation of a SymbolTable for the PySTIL.

'''
import KeyLookUps as KLU

def greetings():
    return "Greetings from PySTIL.SymbolTable"


class SymbolTable(object): 
    '''
    The Symbol table takes in a list of tokens and 
    '''
    
    def __init__(self, tokens, **kwargs): 
        self._map = {} 
        self._semis = []
        self._curlybrackets = []
        self._singleQuotes = []
        self._tokens = tokens 
        # ^^^ TODO: This is nice for bookkeeping instances. However, it is very redundant. 
        # But not really because in Python everything is pass by reference.  
            
        if 'debug' in kwargs: self.debug = kwargs['debug']
        else: self.debug = False 
            
        # st = SymbolTable()
        openCbStack = []; singleQuotes = []; sq = 0 
        for i,token in enumerate(self._tokens):
            _token = token['token']
            _tag = token['tag']
            if _tag in KLU.TopLevel.keywords or _tag in KLU.Other.keywords: 
                self.add_keyword(_tag, i) 
            elif _tag == ';': self._semis.append(i)
            elif _tag == '{': openCbStack.append(i)
            elif _tag == "}": 
                index = openCbStack.pop()
                self._curlybrackets.append((index,i))
            elif _tag == "\'": 
                sq += 1
                if sq%2 == 0: 
                    self._singleQuotes.append((singleQuotes[-1],i))
                    singleQuotes = []
                else: singleQuotes.append(i)
            else: pass 
        # Done with parsing tokens 
    
    def __contains__(self, tag): 
        if tag in self._map: return True
        else: return False 

    def __getitem__(self, keyword): 
        if keyword in self._map: 
            return self._map[keyword]
        else: return []
    # ^^^ NOTE: We return an empty list so that users can 
    # do the following: 
    #   for i in symboltable["BLOCK"]: 
    #       proces on each instance.
        
    def add_keyword(self, tag, i):
        if tag in self._map: 
            self._map[tag].append(i)
        else:
            self._map[tag] = [i]
            
    def __str__(self): 
        retstr = []
        # Keyword storing.
        for tag, values in self._map.items(): 
            retstr.append(" - %s, %s\n"%(tag, values))
        # Curlybrackets storing. 
        retstr.append(" - %s, %s\n"%('{}', self._curlybrackets))
        #for curlygroup in self._curlybrackets: 
        #    retstr.append(" - %s, %s\n"%('{}', curlygroup))
        # Semicolon storing
        retstr.append(" - %s, %s\n"%(';', self._semis))
        # Single quote storing. 
        retstr.append(" - %s, %s\n"%('\'', self._singleQuotes))
        #for sq in self._singleQuotes: 
        #    retstr.append(" - %s, %s\n"%('\'', sq))

        return "".join(retstr)

    def get_list(self, category): 
        if category == "semicolon": 
            return self._semis
        elif category == "single-quotes":
            return self._singleQuotes

        
        else: raise ValueError("Category '%s' is not supported"%(category))
    
    # NOTE: we are passing the tokens around, could make an arg to merge the tokens and
    # the symbol table. 
    def get_next_curly_set(self, startIndex):  
        positives = []
        dictionary = {}
        for i, index in enumerate(self._curlybrackets, start=0):
            tmp = index[0] - startIndex
            if tmp > 0: 
                #print(tmp)
                positives.append(tmp)
                dictionary[tmp] = index
            else : # tmp <= 0:
                pass
        positives.sort()
        return dictionary[positives[0]]
    def get_next_singleQuotes_set(self, startIndex):  
        positives = []
        dictionary = {}
        for i, index in enumerate(self._singleQuotes, start=0):
            tmp = index[0] - startIndex
            if tmp > 0: 
                #print(tmp)
                positives.append(tmp)
                dictionary[tmp] = index
            else : # tmp <= 0:
                pass
        positives.sort()
        return dictionary[positives[0]]

    def get_next_instance(self, startIndex, tag): 
        func = "%s.get_next_instance"%(self.__class__.__name__)
        positives = []
        dictionary = {}
        if tag == ";": 
            for index in self._semis: 
                tmp = index - startIndex
                if tmp > 0: 
                    positives.append(tmp)
                    dictionary[tmp] = index
                else: 
                    pass 
            positives.sort()
            return dictionary[positives[0]]
        

        # This will start at index and move along tokens 
        # until the next instance of tag is found and return 
        # that new index value.
        i = startIndex; iend = len(self._tokens) - 1 
        while i <= iend: 
            if self._tokens[i]['tag'] == tag: 
                return i
            else: i+=1



    def get_next_set(self, startIndex, category):  
        func = "%s.get_next_set"%(self.__class__.__name__)
        positives = []
        dictionary = {}

        if category == "single-quotes": mapp = self._singleQuotes
        elif category == "curly-brackets": mapp = self._curlybrackets
        
        else: raise ValueError("The category '%s' is not supported."%(func, category))

        for i, index in enumerate(mapp, start=0):
            tmp = index[0] - startIndex
            if tmp > 0: 
                #print(tmp)
                positives.append(tmp)
                dictionary[tmp] = index
            else : # tmp <= 0:
                pass
        positives.sort()
        return dictionary[positives[0]]


    def instances_in_range(self, start, end, tag, inclusive=False): 
        """
        By default the range is NON-INCLUSIVE. You can change this by 
        setting the `inclusive` flag to True.
        """
        indexLocations = []
        # If tag is a special character. 
        if tag == "{" or tag == "}": 
            for _start, _end in self._curlybrackets: 
                if not inclusive: 
                    if ((_start > start) and (_end < end )):      
                        indexLocations.append((_start,_end))
                else: 
                    if ((_start >= start) and (_end <= end )):      
                        indexLocations.append((_start,_end))
            return indexLocations

        # If tag was a keyword identifier...
        if tag not in self._map: return indexLocations

        for index in self._map[tag]: 
            if not inclusive: 
                if ((index > start) and (index < end )):      
                    indexLocations.append(index)
            else: 
                if ((index >= start) and (index <= end )):      
                    indexLocations.append(index)
        return indexLocations 

    # NOTE: This is a slightly missed placed utility function. 
    # IT is acting on a token list. I am not sure where to place it becasue the 
    # 'tokens' is merely a list of dictionaries. It is not a 
    # special class. Also, I places it here because the tokens and 
    # symbol table are closely related (the symbol table derives itself
    # from the tokens list.) 
    def string_token_range(self, tokens, start, end, debug = False):
        """
        Note, this range is INCLUSIVE.
        """
        #func = "%s.string_token_range"%(self.__class__.__name__)
        retstr = []

        #if self.debug or debug: 
        #    print("DEBUG: start:%d, end:%d"%(start,end))

        i = start 
        while i <= end: 
            retstr.append(tokens[i]['token'])
            i += 1
        return "".join(retstr)    
    
