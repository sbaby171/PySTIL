import re
import STILutils as sutils
import SymbolTable as STBL
import KeyLookUps as KL


# The idea of the `SpecBlocks` is to keep track of all 
# blocks that may be found throughout the STIL (remeber
# the use of imports). 
# 
# A spec block have has two identifying qualities: 
#   1.) The domain name 
#   2.) The file in which it is associated. 
# 
# NOTE: There is an issue with this. By mandating (2)
# we are implying this can only be used for reading 
# STIL files. Thus, what we does is we not require it. 
# 
# Typically, the SpecBlocks (other classes similiar to 
# it, TimingBlocks, SignalGroupsBlocks, etc.) will be 
# typically used for internal reading processes. 
# 
# Example, if someone wants to add a Spec block to thier 
# STIL object, than they would create it and and us a 
# `stil.add_block()`
# 
# 
class SpecBlocks(sutils.Blocks): 
    def __init__(self): 
        super().__init__()
    def add(self, spec): 
        super().add(spec, Spec)

    # TODO: Refactor the implementation that was done for timing.Wavetables()
    # This is becoming a similiar query structure. 

    # TODO: There is another issue with my implementation. 
    # If i say, `stil.Timings()` (or any other toplevel class)
    # I am always returning a custom object. So when I start doing
    # the following, `stil.Timings().WaveformTables()` where that 
    # returns a list of names, well that is a bit incongruent. 
    # If I was never user, I would expect I was getting another special
    # class. Or at minimum a list od dictionary of the objects. 
    def Categories(self):  
        # NOTE: That below i am just grabbing everything, all the 
        # categoires. Consider this as the most basic implementation
        # adn leave it to users to implement thier own regex searches
        # at the user level. Or create a separate layer API 

        retlist = []
        for spec in self.objects.values(): 
            retlist.extend(list(spec.categories.keys()))
        return retlist






    


# TODO: Technically, based on the syntax of thier examples, the 
# Spec domain name is optional (it is encapsulated within parenthesis).
# Morever, the document states the following, "SPEC_NAME: The name of 
# the spec table. This name is for reference only. It is not used in
# any subsequent references. All defined spec_names shall be unique."
class Spec(object):
    def __init__(self, name = sutils.GLOBAL, file=""): 
        self.name = name 
        self.file = file
        self.categories = {} # TODO: Name->Object
        self.variables  = {} 
        # ^^^ TODO: Get valid sample. Also, it maybe that a spec 
        # block cannt contain both Category and Variable blocks. 
    def add(self, entity): 
        if isinstance(entity, Category): 
            if entity.name in self.categories: 
                raise RuntimeError("Category (%s) is already defined."%(entity.name))
            else: self.categories[entity.name] = entity
        elif isinstance(entity, Variable): 
            if entity.name in self.variables: 
                raise RuntimeError("Variable (%s) is already defined."%(entity.name))
            else: self.variables[entity.name] = entity
        else: 
            raise ValueError("Entity is of to be classes 'Category' or 'Variable'.")
    
    def get_name(self,): return self.name 
    def get_file(self,): return self.file 

    def get_names(self,): # TODO: Trash  
        retdict = {}
        for cat in self.categories: 
            retdict[cat] = 'Category'
        for var in self.variables: 
            retdict[var] = 'Variables'
        return retdict
    def get_categories(self,): 
        return self.categories

    def category(self, name): 
        if name not in self.categories: 
            raise ValueError("The Category (%s) is not present."%(name))
        return self.categories[name]
    # TODO: def variable(self, name): 


class Category(object): 
    def __init__(self, name="", spec=""): 
        self.name = name 
        self.spec = spec 
        # ^^^ NOTE: It is optional for the Category to maintain 
        # its parent reference. This optionality is to allow for 
        # completely modular developement. However, it is imporant
        # this can complicate later processes and maintence. 
        # Morever, a valid question would be, "But if a Category
        # block is only ever defined within a Spec block, it makes
        # no sense to not provide this link." The only rebuttle to 
        # that would be in terms of a STIL writer. That is I may
        # want to reuse my Category block across many Spec instances.  
        self.vars = {} # varName -> {Min, Typ, Max, Direct}

    def add(self,var,value="",Min="",Max="",Typ="", debug=False):  
        if var in self.vars: 
            #raise RuntimeError("Variable %s is already set."%(var))
            if debug: print("Variable %s is already set."%(var))
            return 
        tmpDict = {} 
        if Min: tmpDict['Min'] = Min
        if Typ: tmpDict['Typ'] = Typ
        if Max: tmpDict['Max'] = Max
        if value: 
            if tmpDict: 
                raise ValueError("If value is provided, we cannot also set Min, Typ, or Max.")
            else: tmpDict['value'] = value
        if not tmpDict:  
            raise ValueError("Must provide atleast value, Min, Typ, or Max")
        if var in self.vars: 
            raise RuntimeError("Var (%s) is already defined."%(var))
        self.vars[var] = tmpDict


    def __len__(self,): 
        return len(self.vars)

    def __str__(self,): 
        retstr = ["Category: %s"%(self.name)]
        for var in self.vars: 
            retstr.append(" - %s: %s"%(var, self.vars[var]))
        return "\n".join(retstr)

class Variable(object): 
    def __init__(self, name, spec=""): 
        self.name = name 
        self.spec = spec 
        # ^^^ NOTE: It is optional for the Category to maintain 
        # its parent reference. This optionality is to allow for 
        # completely modular developement. However, it is imporant
        # this can complicate later processes and maintence. 
        # Morever, a valid question would be, "But if a Category
        # block is only ever defined within a Spec block, it makes
        # no sense to not provide this link." The only rebuttle to 
        # that would be in terms of a STIL writer. That is I may
        # want to reuse my Category block across many Spec instances.  
        self.cats = {} # catName -> {Min, Typ, Max, Direct}

# TODO: See how the structure of the Category block and Variable
# blocks are so similiar. The question is then, "Do you create a 
# refactored based class by which both blocks 'inherit' from"? 
# Refer to my notes on this answer.



def create_spec(string, name = "", file = "", debug=False):
    """ 
    String is a raw string. Typically this will be coming from the 
    STIL object. 
    """
    func   = "create_spec"
    tokens = sutils.lex(string=string, debug=debug)
    sytbl  = STBL.SymbolTable(tokens=tokens, debug=debug) 
    spec   = Spec(name=name, file=file)
    if debug: 
        print("DEBUG: (%s): Tokens: %s "% (func, tokens))
        print("DEBUG: (%s): SymbolTable: %s"%(func, sytbl))

    if 'Category' in sytbl: 
        for index in sytbl["Category"]: 
            cbs, cbe = sytbl.get_next_curly_set(index)
            if cbs - index != 2: 
                raise RuntimeError("Expecting 'Spec <name> {'")
            category = Category()
            category.name = tokens[index + 1]['token']
            i = cbs + 1; end = cbe - 1
            while i <= end: 
                if tokens[i+1]['tag'] == "{": 
                    settings = {}
                    name = tokens[i]['token']
                    _cbs, _cbe = sytbl.get_next_curly_set(i)

                    if ((tokens[i+2]['tag'] == "Min") or 
                        (tokens[i+2]['tag'] == "Typ") or 
                        (tokens[i+2]['tag'] == "Max")):
                        semi = sytbl.get_next_instance(i+2, ';')
                        settings[tokens[i+2]['tag']]  = sytbl.string_token_range(tokens, i+3, semi-1)

                        if semi == _cbe - 1: 
                            raise RuntimeError("Havent implemented yet.")

                        if ((tokens[semi+1]['tag'] == "Min") or 
                            (tokens[semi+1]['tag'] == "Typ") or 
                            (tokens[semi+1]['tag'] == "Max")):
                            oldSemi = semi
                            semi = sytbl.get_next_instance(semi+2, ';')
                            settings[tokens[oldSemi+1]['tag']]  = sytbl.string_token_range(tokens, oldSemi+2, semi-1)

                            if semi == _cbe - 1: 
                                raise RuntimeError("Havent implemented yet.")


                            if ((tokens[semi+1]['tag'] == "Min") or 
                                (tokens[semi+1]['tag'] == "Typ") or 
                                (tokens[semi+1]['tag'] == "Max")):
                                oldSemi = semi
                                semi = sytbl.get_next_instance(semi+2, ';')
                                settings[tokens[oldSemi+1]['tag']]  = sytbl.string_token_range(tokens, oldSemi+2, semi-1)

                                if semi == _cbe - 1: 
                                    minValue = None; typValue = None; maxValue = None
                                    if 'Min' in settings: minValue = settings["Min"]
                                    if 'Typ' in settings: typValue = settings["Typ"]
                                    if 'Max' in settings: maxValue = settings["Max"]
                                    category.add(name, Min=minValue, Typ=typValue, Max=maxValue)
                                else: 
                                    raise RuntimeError("Expecting the spec variable to be finished now.")
                    else: 
                        raise RuntimeError("Expecting a Min, Typ, or Max settings.")

                if tokens[i+1]['tag'] == "=": 
                    if tokens[i]['tag'] != 'identifier': 
                        raise RuntimeError("Expecting name of spec to be 'identifier'")
                    name = tokens[i]['token']
                    semi = sytbl.get_next_instance(i, ';')
                    value = sytbl.string_token_range(tokens, i+2, semi-1)
                    category.add(name, value)
                    i = semi + 1
                    continue  
                i+=1
            spec.add(category)

    if 'Variable' in sytbl: 
        raise RuntimeError("The implementation for Spec 'Variable' is no done.")
        # TODO: Overload Variable creation to other method. 
    # TODO: Perhaps the Variable and Category builders can 
    # be of the same method? 
    return spec

class SelectorBlocks(object): 
    def __init__(self): 
        self.selectors = {} # Name -> SpecObject
    def add(self, selector): 
        if not isinstance(selector, Selector): 
            raise ValueError("Must provide instance of Selector.")
        if selector.name in self.selectors: 
            raise ValueError("Spec %s is already defined"%(selector.name)) 
        self.selectors[selector.name] = selector
    def selector(self, name): 
        if name in self.selectors: return self.selectors[name]
        else: return None
    def __len__(self): 
        return len(self.selectors)

class Selector(object): 

    def __init__(self, name): 
        self.name = name 
        self.vars = {} # varName -> Min|Typ|Max|Meas
    
    def add(self, var, value): 
        if var in self.vars: 
            raise RuntimeError("Variable %s is already set."%(var))
        if value not in ["Min",'Typ','Max','Meas']: 
            raise RuntimeError("Bad value %s. Only Min, Typ, Max, and Meas are allowed."%(value))
        self.vars[var] = value 
    
    def __len__(self): 
        return len(self.vars)

    



def create_selector(string, name = "", file = "", debug=False):
    """ 
    String is a raw string. Typically this will be coming from the 
    STIL object. 
    """
    func   = "create_selector"
    tokens = sutils.lex(string=string, debug=debug)
    sytbl  = STBL.SymbolTable(tokens=tokens, debug=debug) 
    spec   = Spec(name=name)
    if debug: 
        print("DEBUG: (%s): Tokens: %s "% (func, tokens))
        print("DEBUG: (%s): SymbolTable: %s"%(func, sytbl))

    if 'Selector' not in sytbl: 
        raise ValueError("No Selectors in symbol table.") # TODO: It is not clear that this should be an error. 
    else: 
        selector = Selector(name=name)
        if len(sytbl["Selector"]) >= 2: 
            raise RuntimeError("Not expecting more than one Selector item")
        index = sytbl["Selector"][0]
        cbs, cbe = sytbl.get_next_curly_set(index)
        if cbs - index != 2: 
            raise RuntimeError("Expecting 'Selector <name> {'")
        if name != tokens[index+1]['token']: 
            raise RuntimeError("Selector names do not match. %s != %s"%(name, tokens[index+1]['token']))
        i = cbs + 1; end = cbe - 1
        while i <= end: 
            if tokens[i]['tag'] != 'identifier': 
                raise RuntimeError("Expecting identifier.")
            varName = tokens[i]['token']
            if tokens[i+1]['tag'] not in ['Min', 'Typ', 'Max','Meas']: #TODO: Reference a global look up
                raise RuntimeError("Expecting either 'Min', 'Typ', 'Max', or 'Meas'")
            value = tokens[i+1]['token']
            if tokens[i+2]['tag'] != ';': 
                raise RuntimeError("Expecting semicolon to end statement.")
            selector.add(varName,value)
            i+=3; continue 
    return selector
         
                    
   





        
# ============================================================================: 
# Documentation and Notes: 
# ============================================================================: 
# 4.0) Structure of this standard: 
# In the syntax deinftions: 
#   d) () indicated optional syntax which may be used 0 or 1 time. 
#
# 19.0) Spec and Selector blocks: 
# Spec blocks are used to define the value of the variables and 
# expressions that are used within the waveform definitions. Each 
# Spec block may contain Category blocks (which contain spec variable
# definitions) or Variable definitions. 