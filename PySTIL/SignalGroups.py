import re
import STILutils as sutils
import SymbolTable as STBL
import KeyLookUps as KLU

class SignalGroupsBlocks(sutils.Blocks): 
    def __init__(self): 
        super(SignalGroupsBlocks, self).__init__()
    def add(self, signalGroups): 
        super(SignalGroupsBlocks, self).add(signalGroups, SignalGroups)


class SignalGroups(object): 
    def __init__(self, name, mapping, file=""): 

        self.file = file
        self.name = name
        self._mapping = mapping


    def get_name(self, ):
        return self.name 
    
    def get_file(self, ): 
        return self.file


    
    def get_signals(self, group):
        """Given a group, return the signals defintion"""
        if group in self._mapping: 
            return self._mapping[group]
        else: return []
 
    def group(self, group): 
        """This returns the single specific instance of the group."""
        if group in self._mapping: 
            return self._mapping[group]
        else: return None

    # TODO: Add regex for group names? 
    def groups(self, signal=""): 
        """ Return a list of groups.

        If signal is provided, only those groups containing the signal will
        be returned. Note, `signal` is not a regex. 

        If signal is not provided, then all groups are returned. 
        """
        retlist = []
        if not signal: return list(self._mapping.keys())
        for group in self._mapping: 
            if signal in self._mapping[group]['signals']:
                retlist.append(group) 
        return retlist
    
    def group_names(self,):
        """Return a list of all the group names."""
        return list(self._mapping.keys())


    # TODO: Extend to N number if needed.....
    def find_common_and_diff_signals(self, group1, group2): 
        """Find the common and different signals between two groups."""
        if group1 not in self._mapping: 
            raise ValueError("Group %s is not present."%(group1))
        if group2 not in self._mapping: 
            raise ValueError("Group %s is not present."%(group2))

        signalList1 = self._mapping[group1]["signals"]
        signalList2 = self._mapping[group2]["signals"]
        common = []
        diff = []

        i = 0; iend = len(signalList1) - 1
        j = 0; jend = len(signalList2) - 1
        while i <= iend: 
            signal1 = signalList1[i]
            j = 0; 
            while j <= jend: 
                if signal1 == signalList2[j]: 
                    common.append(signal1)
                    del signalList2[j]
                    j = jend + 1; continue
                else: 
                    if j == jend: 
                        diff.append(signal1)
                j+=1 
            i += 1
        
        # Update what ever is left in signalList2 to diff 
        diff.extend(signalList2)
        return common , diff 


# TODO: This doesn't have to be a static method. It merely be a funciton.
def create_signalGroups(string, name = "", file = "", debug=False):
    func = "SignalGroups.create_signalGroups"
    tokens = sutils.lex(string=string, debug=debug)
    sytbl  = STBL.SymbolTable(tokens=tokens, debug=debug) 

    if debug: 
        print("DEBUG: (%s): Tokens: %s "% (func, tokens))
        print("DEBUG: (%s): SymbolTable: %s"%(func, sytbl))

    signalGroups = {}
    signalGroupName = ""

    if not name:
        _start, _end = sytbl.get_next_set(0, 'curly-brackets')
        if _start == 1:   name = KLU.References.GLOBAL
        elif _start == 2: name = tokens[1]["token"]
        else: raise ValueError("Unable to extract domain-name.")
    else: 
        if debug: print("DEBUG: (%s): Received domain name: %s"%(func, name))

    # Get list of single quote parings: 
    singleQuotePairs = sytbl.get_list(category="single-quotes")
    i = 0; end = len(singleQuotePairs) - 1; 

    while i <= end: 
        signalGroupName = ""
        signalGroupSignals = []
        _start, _end = singleQuotePairs[i]
        # TODO: Can place some sanity checks here: length= 1|3|5|etc. even not allowed

        # NOTE: Evaluate left side: extract signalGroup name
        if tokens[_start-1]['tag'] != '=': 
            raise SyntaxError("Must invalid syntax: Expected '='.")
        if tokens[_start-2]['tag'] != 'identifier': 
            raise SyntaxError("Must invalid syntax: Expected signal group name.")
        else: signalGroupName = tokens[_start-2]['token']
        if debug: print("DEBUG: (%s): Found signalgroup name: %s"%(func, signalGroupName))

        # NOTE: Check contents:
        j = _start + 1; jend = _end - 1
        while j <= jend : 
            if j == (_start + 1): # First element
                if tokens[j]['tag'] != 'identifier':  raise SyntaxError("Expecting an identifier")
                entity = tokens[j]['token']
                if entity in signalGroups: 
                    entity = signalGroups[entity]["signals"]
                    if debug: print("DEBUG: (%s): Found a group name within content '%s', Expandng to '%s'"%(func, tokens[j]['token'], entity))
                    signalGroupSignals += entity 
                else: 
                    signalGroupSignals.append(entity)
                    j+=1; continue

            if tokens[j]['tag'] == '+': 
                if tokens[j+1]['tag'] != 'identifier': raise SyntaxError("An identifier must follow a '+'.")
                entity = tokens[j+1]['token']
                if entity in signalGroups: 
                    entity = signalGroups[entity]["signals"]
                    if debug: print("DEBUG: (%s): Found a group name within content '%s', Expandng to '%s'"%(func, tokens[j]['token'], entity))
                    signalGroupSignals += entity 
                else: 
                    signalGroupSignals.append(entity)
                j += 2; continue

            if tokens[j]['tag'] == '-': 
                if tokens[j+1]['tag'] != 'identifier': raise SyntaxError("An identifier must follow a '+'.")
                entity = tokens[j+1]['token']
                if entity in signalGroups: 
                    entity = signalGroups[entity]["signals"]
                    if debug: print("DEBUG: (%s): Found a group name within content '%s', Expandng to '%s'"%(func, tokens[j]['token'], entity))
                    for substractSignal in entity: 
                        signalGroupSignals.remove(substractSignal)
                else: 
                    signalGroupSignals.remove(entity)
                j += 2; continue
                
            j+=1

        # NOTE: Check right-hand side: 
        if tokens[_end+1]['tag'] == ';': 
            if signalGroupName == "": raise RuntimeError("SignalGroup name is not set.")
            if signalGroupSignals == []: raise RuntimeError("SignalGroup list is empty.")
            signalGroups[signalGroupName] = {"signals": signalGroupSignals, 
                                             "properties" : {}}
            if debug: print("DEBUG: (%s): Added '%s' to signalGroups: %s"%(func, signalGroupName, signalGroups[signalGroupName]))

        elif tokens[_end+1]['tag'] == '{': 
            #print("Continuing")
            # TODO: Grab next set of curly....
            cs , ce = sytbl.get_next_set(_end, category='curly-brackets')
            j = cs + 1; jend = ce -1; 
            while (j <= jend): 
                if tokens[j]['tag'] == "Base": 
                    if tokens[j+1]['tag'] == "Hex" or tokens[j+1]['tag'] == "Dec": 
                        if tokens[j+2]['tag'] == 'identifier': 
                            if tokens[j+3]['tag'] == ';':
                                if signalGroupName == "": raise RuntimeError("SignalGroup name is not set.")
                                if signalGroupSignals == []: raise RuntimeError("SignalGroup list is empty.")
                                if signalGroupName in signalGroups:
                                    signalGroups[signalGroupName]['properties']['Base'] = [tokens[j+1]['token'], tokens[j+2]['token']]
                                    if debug: print("DEBUG: (%s): Added 'Base' to signal %s' to signalGroups: %s"%(func, signalGroupName, signalGroups[signalGroupName]))
                                else: 
                                    signalGroups[signalGroupName] = {"signals": signalGroupSignals, 
                                    "properties" : {
                                        "Base": [tokens[j+1]['token'], tokens[j+2]['token']]
                                    }}
                                    if debug: print("DEBUG: (%s): Added '%s' to signalGroups: %s"%(func, signalGroupName, signalGroups[signalGroupName]))
                                j += 4; continue
                            else: raise SyntaxError("Base needs to be terminated with semicolon.")
                        else: raise SyntaxError("Base needs waveform characters.")
                    else: raise SyntaxError("Expecting 'Hex' or 'Dec' directly after 'Base'.")

                if tokens[j]['tag'] == 'Alignment': 
                    if tokens[j+1]['tag'] == 'MSB' or tokens[j+1]['tag'] == 'LSB': 
                        if tokens[j+2]['tag'] == ';': 
                            if signalGroupName == "": raise RuntimeError("SignalGroup name is not set.")
                            if signalGroupSignals == []: raise RuntimeError("SignalGroup list is empty.")
                            if signalGroupName in signalGroups:
                                signalGroups[signalGroupName]['properties']['Alignment'] = tokens[j+1]['token']
                                if debug: print("DEBUG: (%s): Added 'Alignment' to signal %s' to signalGroups: %s"%(func, signalGroupName, signalGroups[signalGroupName]))
                            else: 
                                signalGroups[signalGroupName] = {"signals": signalGroupSignals, 
                                    "properties" : {
                                        "Alignment": tokens[j+1]
                                    }}
                                if debug: print("DEBUG: (%s): Added '%s' to signalGroups: %s"%(func, signalGroupName, signalGroups[signalGroupName]))
                            j += 3; continue
                        else: raise SyntaxError("Alignment must end in semicolon")
                    else: raise SyntaxError("Alignment is only allowed 'MSB' or 'LSB'")
                
                if tokens[j]['tag'] == "ScanOut":
                    if tokens[j+1]['tag'] == "digits": 
                        if tokens[j+2]['tag'] == ';':  
                            if signalGroupName == "": raise RuntimeError("SignalGroup name is not set.")
                            if signalGroupSignals == []: raise RuntimeError("SignalGroup list is empty.")
                            if signalGroupName in signalGroups:
                                signalGroups[signalGroupName]['properties']['ScanOut'] = tokens[j+1]['token']
                                if debug: print("DEBUG: (%s): Added 'ScanOut' to signal %s' to signalGroups: %s"%(func, signalGroupName, signalGroups[signalGroupName]))
                            else: 
                                signalGroups[signalGroupName] = {"signals": signalGroupSignals, 
                                    "properties" : {
                                        "ScanOut": tokens[j+1]['token']
                                    }}
                                if debug: print("DEBUG: (%s): Added '%s' to signalGroups: %s"%(func, signalGroupName, signalGroups[signalGroupName]))
                            j += 3; continue
                        else: raise SyntaxError("Alignment must end in semicolon")
                    elif tokens[j+1]['tag'] == ';': 
                        if signalGroupName == "": raise RuntimeError("SignalGroup name is not set.")
                        if signalGroupSignals == []: raise RuntimeError("SignalGroup list is empty.")
                        if signalGroupName in signalGroups:
                            signalGroups[signalGroupName]['properties']['ScanOut'] = True
                            if debug: print("DEBUG: (%s): Added 'ScanOut' to signal %s' to signalGroups: %s"%(func, signalGroupName, signalGroups[signalGroupName]))
                        else: 
                            signalGroups[signalGroupName] = {"signals": signalGroupSignals, 
                                    "properties" : {
                                        "ScanOut": True
                                }}
                            if debug: print("DEBUG: (%s): Added '%s' to signalGroups: %s"%(func, signalGroupName, signalGroups[signalGroupName]))
                        j += 2; continue
                    else: raise SyntaxError("Expecting ; or digit after ScanOut")
                j += 1
        else: raise SyntaxError("Expected ';' or '{'")
        i += 1
    if debug: 
        for grp in signalGroups: 
            print("DEBUG: (%s): Signal Group: %s"%(func, grp))
            print("DEBUG: (%s):   -> %s"%(func, signalGroups[grp]))

    return SignalGroups(name = name, file = file, mapping = signalGroups)
