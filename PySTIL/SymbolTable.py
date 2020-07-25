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

    def __getitem__(self, keyword): 
        if keyword in self._map: 
            return self._map[keyword]
        else: return None
        
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
        for curlygroup in self._curlybrackets: 
            retstr.append(" - %s, %s\n"%('{}', curlygroup))
        # Semicolon storing
        retstr.append(" - %s, %s\n"%(';', self._semis))
        # Single quote storing. 
        for sq in self._singleQuotes: 
            retstr.append(" - %s, %s\n"%('\'', sq))
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
    