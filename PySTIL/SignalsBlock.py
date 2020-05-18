"""
PySTIL sub module to handle the Signals block. 
"""


class Signal(object):
    def __init__(self,*args,**kwargs):
        if "name" in kwargs: self.name = kwargs["name"]
        else: self.name = ""
        if "type" in kwargs: self.type = kwargs["type"]
        else: self.type = ""
        # other feilds.

    def get_name(self): 
        return self.name

    def __str__(self): 
        retstr = [self.name, ", ", self.type]

        return "".join(retstr)

class Signals(object): 
    def __init__(self,*args,**kwargs): 
        self._name_to_signal = {}
        self._shorthand_ref = []

    def add_shorthand_ref(self,value): 
        self._shorthand_ref.append(value)

    def add(self,signal ):
        if not isinstance(signal, Signal): 
            raise ValueError("Must provide a Signal type")
        if signal.name in self._name_to_signal: 
            raise ValueError("Signal has already been added: ", signal.name)
        else: 
            self._name_to_signal[signal.name] = signal
        return 
    
    def __getitem__(self, name): 
        if name in self._name_to_signal: 
            return self._name_to_signal[name]
        else: 
            raise IndexError("No signal with the following name: ",name)
    def __iter__(self): 
        for name in self._name_to_signal.keys(): 
            yield self._name_to_signal[name]

    def __len__(self): 
        return len(self._name_to_signal)

    def __str__(self): 
        retstr = ["Signals: \n",
                  "------------- \n"]
        for name, signal in self._name_to_signal.items(): 
            retstr.append(str(signal) + "\n") 

        if self._shorthand_ref: 
            retstr.append("\n  Shorthard references:\n")
            for entry in self._shorthand_ref: 
                retstr.append("  "+str(entry) + "\n") 

        return "".join(retstr)