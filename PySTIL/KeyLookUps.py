"""
This file is more than STILkeywords; so in that regard, this file is a bit 
of a misnomer. 

It mainly holds keycharacters and keyworks that are used within the lexical 
analysis, parsing, and other processes of PySTIL (i.e. translation od data 
to intermediate representation). 

"""

import re
# The References, TopLevel, and Other can be used in may stages of the processing. 
# That is, during the lexer, the parser, or translation to an intermediate file type. 
def greetings(): return "Greetings from PySTIL.KeyLookUps"

class References(object): 
    lower  = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'] 
    upper  = ['A','B','C','D','E','F','G','H','I','j','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    number = ['0','1','2','3','4','5','6','7','8','9']
    alphanumeric = lower + upper + number + ['_']
    re_digits = re.compile("^\d+$")
    spaces = [' ', '\n', '\t']
    # special chars: see page 59 in STIL std. (PDF 67)
    special = [';','.','{','}','-','+','!','@','#','$','%','^','&','*',
               '(',')','=','|','`','~','[',']',':','<','>','.',',',
              '\'', # TODO: This may need to move... 
              ]

    GLOBAL = ' '# This is to help with identifiy global domain names.
    # Include

    

class TopLevel(object):
    keywords = {"STIL":re.compile("^STIL$"), 
                "Include": re.compile("^Include$"),
                "Header": re.compile("^Header$"), 
                "Signals": re.compile("^Signals$"), 
                "SignalGroups": re.compile("^SignalGroups$"), 
                "ScanStructures": re.compile("^ScanStructures$"), 
                "Spec": re.compile("^Spec$"),
                "Timing": re.compile("^Timing$"), 
                "Selector": re.compile("^Selector$"),
                "PatternBurst": re.compile("^PatternBurst$"), 
                "PatternExec": re.compile("^PatternExec$"), 
                "Procedures": re.compile("^Procedures$"), 
                "MacroDefs": re.compile("^MacroDefs$"),
                "Pattern": re.compile("^Pattern$"),
                "UserKeywords": re.compile("^UserKeywords$"),
                "UserFunctions": re.compile("^UserFunctions$"),
                "Ann": re.compile("^Ann$"), # TODO: This is in both TopLevel and Others. Becareful.
                "DCLevels": re.compile("^DCLevels$"),
                "DCSets": re.compile("^DCSets$"),
                "DCSequence": re.compile("^DCSequence$"),
                "Environment": re.compile("^Environment$")
                }
    
class Other(object): 
    keywords = {"A": re.compile("^A$"), 
                "Alignment": re.compile("^Alignment$"),
                "Ann": re.compile("^Ann$"),
                "Apply": re.compile("^Apply$"), # DCLevels, 
                "B": re.compile("^B$"),
                "Base": re.compile("^Base$"),
                "BreakPoint": re.compile("^BreakPoint$"),
                "Call": re.compile("^Call$"),
                "Category": re.compile("^Category$"),
                "Clamp": re.compile("^Clamp$"), # DcLevels
                "ClampHi": re.compile("^ClampHi$"), # DcLevels
                "ClampLo": re.compile("^ClampLo$"), # DcLevels
                "Comparator": re.compile("^Comparator$"), # DcLevels
                "CompareHigh": re.compile("^CompareHigh$"),
                "CompareHighWindow": re.compile("^CompareHighWindow$"),
                "CompareLow": re.compile("^CompareLow$"),
                "CompareLowWindow": re.compile("^CompareLowWindow$"),
                "CompareUnknown": re.compile("^CompareUnknown$"),
                "CompareValid": re.compile("^CompareValid$"),
                "CompareValidWindow": re.compile("^CompareValidWindow$"),
                "CompareZ": re.compile("^CompareZ$"),
                "CompareZWindow": re.compile("^CompareZWindow$"),
                "Condition": re.compile("^Condition$"),
                "Connect": re.compile("^Connect$"), # DcLevels
                "D": re.compile("^D$"),
                "DataBitCount": re.compile("^DataBitCount$"), 
                "Date": re.compile("^Date$"), 
                "Dec": re.compile("^Dec$"),
                "DefaultState": re.compile("^DefaultState$"),
                "EndOfProgram": re.compile("^EndOfProgram$"), # DcLevels
                "ExceptHigh": re.compile("^ExceptHigh$"),
                "ExceptLow": re.compile("^ExceptLow$"),
                "ExceptOff": re.compile("^ExceptOff$"),
                "F": re.compile("^F$"),
                "ForceDown": re.compile("^ForceDown$"),
                "ForceHi": re.compile("^ForceHi$"),# DcLevels
                "ForceLo": re.compile("^ForceLo$"),# DcLevels
                "ForceOff": re.compile("^ForceOff$"),
                "ForcePrior": re.compile("^ForcePrior$"),
                "ForceUnknown": re.compile("^ForceUnknown$"),
                "ForceUp": re.compile("^ForceUp$"),
                "G": re.compile("^G$"),
                "Goto": re.compile("^Goto$"),
                "H": re.compile("^H$"),
                "Hex": re.compile("^Hex$"),
                "History": re.compile("^History$"),
                "IClamp": re.compile("^IClamp$"), # DcLevels
                "IForce": re.compile("^IForce$"), # DcLevels
                "InheritDCLevels": re.compile("^InheritDCLevels$"), # DcLevels
                "InitHi": re.compile("^InitHi$"), # DcLevels
                "InitialSetup": re.compile("^InitialSetup$"), # DcLevels
                "InitLo": re.compile("^InitLo$"), # DcLevels
                "IOH": re.compile("^IOH$"), # DcLevels
                "IOL": re.compile("^IOL$"), # DcLevels
                "IDDQTestPoint": re.compile("^IDDQTestPoint$"), # TODO: Verify
                "IfNeed": re.compile("^IfNeed$"),
                "In": re.compile("^In$"), 
                "Infinite": re.compile("^Infinite$"),
                "InheritWaveform": re.compile("^InheritWaveform$"),
                "InheritWaveformTable": re.compile("^InheritWaveformTable$"),
                "InOut": re.compile("^InOut$"), 
                "L": re.compile("^L$"), 
                "Load": re.compile("^Load$"), # DCLevels 
                "LoadVRef": re.compile("^LoadVRef$"), # DCLevels 
                "LogicHigh": re.compile("^LogicHigh$"),
                "LogicLow": re.compile("^LogicLow$"),
                "LogicZ": re.compile("^LogicZ$"),
                "Loop": re.compile("^Loop$"),
                "LSB": re.compile("^LSB$"),
                "M": re.compile("^M$"),
                "Macro": re.compile("^Macro$"),
                "Marker": re.compile("^Marker$"),
                "MatchLoop": re.compile("^matchLoop$"),
                "Max": re.compile("^Max$"),
                "Meas": re.compile("^Meas$"),
                "Min": re.compile("^Min$"),
                "MSB": re.compile("^MSB$"),
                "N": re.compile("^N$"),
                "Loop": re.compile("^Loop$"),
                "Out": re.compile("^Out$"), 
                "P": re.compile("^P$"),
                "PatList": re.compile("^PatList$"),
                "PatSet":re.compile("^PatSet$"), # 1450.1
                "ParallelPatList": re.compile("^ParallelPatList$"), # 1450.1
                "SyncStart": re.compile("^SyncStart$"), # 1450.1
                "Independent": re.compile("^Independent$"), # 1450.1
                "LockStep": re.compile("^LockStep$"), # 1450.1
                "Extend": re.compile("^Extend$"), # 1450.1
                "Period": re.compile("^Period$"),
                "PMU": re.compile("^PMU$"), # DCLevels
                "PowerLower": re.compile("^PowerLower$"), # DCLevels
                "PowerRaise": re.compile("^PowerRaise$"), # DCLevels
                "Procedures": re.compile("^Procedures$"),
                "Pseudo": re.compile("^Pseudo$"),
                "Q": re.compile("^Q$"),
                "R": re.compile("^R$"),
                "Ramp": re.compile("^Ramp$"), # DCLevels
                "ResistiveTermination": re.compile("^ResistiveTermination$"), # DCLevels
                "ScanCells": re.compile("^ScanCells$"),
                "ScanChain": re.compile("^ScanChain$"),
                "ScanIn": re.compile("^ScanIn$"),
                "ScanInversion": re.compile("^ScanInversion$"),
                "ScanLength": re.compile("^ScanLength$"),
                "ScanMasterClock": re.compile("^ScanMasterClock$"),
                "ScanOut": re.compile("^ScanOut$"),
                "ScanOutLength": re.compile("^ScanOutLength$"),
                "ScanSlaveClock": re.compile("^ScanSlaveClock$"),
                "ScanSlaveClock": re.compile("^ScanSlaveClock$"),
                "Shift": re.compile("^Shift$"), 
                "Source": re.compile("^Source$"), 
                "Start": re.compile("^Start$"), 
                "Stop": re.compile("^Stop$"),
                "SubWaveforms": re.compile("^SubWaveforms$"),
                "Supply": re.compile("^Supply$"),
                "T": re.compile("^T$"),
                "TerminateHigh": re.compile("^TerminateHigh$"),
                "TerminateLow": re.compile("^TerminateLow$"),
                "TerminateOff": re.compile("^TerminateOff$"),
                "TerminateUnknown": re.compile("^TerminateUnknown$"),
                "Termination": re.compile("^Termination$"),
                "TermVRef": re.compile("^TermVRef$"), # DCLevels
                "TimeUnit": re.compile("^TimeUnit$"),
                "Title": re.compile("^Title$"), 
                "Typ": re.compile("^Typ$"),
                "U": re.compile("^U$"),
                "User": re.compile("^User$"), # DCLevels
                "Unknown": re.compile("^Unknown$"),
                "V": re.compile("^V$"), 
                "VClamp": re.compile("^VClamp$"), #DCLevels 
                "VForce": re.compile("^VForce$"), #DCLevels 
                "VICM": re.compile("^VICM$"), #DCLevels 
                "VID": re.compile("^VID$"), #DCLevels 
                "VIH": re.compile("^VIH$"), #DCLevels 
                "VIHD": re.compile("^VIHD$"), #DCLevels 
                "VIHSlew": re.compile("^VIHSlew$"), #DCLevels 
                "VIL": re.compile("^VIL$"), #DCLevels 
                "VIHL": re.compile("^VIHL$"), #DCLevels 
                "VILSlew": re.compile("^VILSlew$"), #DCLevels 
                "VOCM": re.compile("^VOCM$"), #DCLevels 
                "VOD": re.compile("^VOD$"), #DCLevels 
                "VOH": re.compile("^VOH$"), #DCLevels 
                "VOHD": re.compile("^VOHD$"), #DCLevels 
                "VOL": re.compile("^VOL$"), #DCLevels 
                "VOLD": re.compile("^VOLD$"), #DCLevels 
                "Variable": re.compile("^Variable$"),
                "Vector": re.compile("^Vector$"),
                "W": re.compile("^W$"), 
                "Waveforms": re.compile("^Waveforms$"), 
                "WaveformTable": re.compile("^WaveformTable$"),
                "X": re.compile("^X$"),
                "Z": re.compile("^Z$"),
               }


all_keys = list(TopLevel.keywords.keys()) + list(Other.keywords.keys())