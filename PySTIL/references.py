import re
GLOBAL_DOMAIN = "__GLOBAL__"

TOP_LEVEL_KEYWORDS = set([
  "STIL", 
  "Include", 
  "Header", 
  #"Ann" # Ignoring for now becaue it would be caught w/in other blocks!
  "Signals", 
  "SignalGroups",
  "ScanStructures", 
  "Spec", 
  "DCLevels",
  "DCSets", 
  "Timing", 
  "Selector", 
  "PatternBurst", 
  "PatternExec", 
  "Procedures", 
  "MacroDefs",
  "Environment", 
  "PatternFailReport", 
  "Pragma", 
  "UserKeywords",
  "UserFunctions",
  "Pattern"
])
OTHER_KEYWORDS = set([
  "A", 
  "Alignment",
  "Ann",
  "Apply",# DCLevels, 
  "B",
  "Base",
  "BreakPoint",
  "Call",
  "Category",
  "Clamp", # DcLevels
  "ClampHi", # DcLevels
  "ClampLo", # DcLevels
  "Comparator", # DcLevels
  "CompareHigh",
  "CompareHighWindow",
  "CompareLow",
  "CompareLowWindow",
  "CompareUnknown",
  "CompareValid",
  "CompareValidWindow",
  "CompareZ",
  "CompareZWindow",
  "Condition",
  "Connect", # DcLevels
  "D",
  "DataBitCount", 
  "Date", 
  "Dec",
  "DefaultState",
  "EndOfProgram", # DcLevels
  "ExceptHigh",
  "ExceptLow",
  "ExceptOff",
  "F",
  "ForceDown",
  "ForceHi",# DcLevels
  "ForceLo",# DcLevels
  "ForceOff",
  "ForcePrior",
  "ForceUnknown",
  "ForceUp",
  "G",
  "Goto",
  "H",
  "Hex",
  "History",
  "IClamp", # DcLevels
  "IForce", # DcLevels
  "InheritDCLevels", # DcLevels
  "InitHi", # DcLevels
  "InitialSetup", # DcLevels
  "InitLo", # DcLevels
  "IOH", # DcLevels
  "IOL", # DcLevels
  "IDDQTestPoint", # TODO: Verify
  "IfNeed",
  "In", 
  "Infinite",
  "InheritWaveform",
  "InheritWaveformTable",
  "InOut", 
  "L", 
  "Load", # DCLevels 
  "LoadVRef", # DCLevels 
  "LogicHigh",
  "LogicLow",
  "LogicZ",
  "Loop",
  "LSB",
  "M",
  "Macro",
  "Marker",
  "MatchLoop",
  "Max",
  "Meas",
  "Min",
  "MSB",
  "N",
  "Loop",
  "Out", 
  "P",
  "PatList",
  "PatSet", # 1450.1
  "ParallelPatList", # 1450.1
  "SyncStart", # 1450.1
  "Independent", # 1450.1
  "LockStep", # 1450.1
  "Extend", # 1450.1
  "Period",
  "PMU", # DCLevels
  "PowerLower", # DCLevels
  "PowerRaise", # DCLevels
  "Procedures",
  "Pseudo",
  "Q",
  "R",
  "Ramp", # DCLevels
  "ResistiveTermination", # DCLevels
  "ScanCells",
  "ScanChain",
  "ScanIn",
  "ScanInversion",
  "ScanLength",
  "ScanMasterClock",
  "ScanOut",
  "ScanOutLength",
  "ScanSlaveClock",
  "ScanSlaveClock",
  "Shift", 
  "Source", 
  "Start", 
  "Stop",
  "SubWaveforms",
  "Supply",
  "T",
  "TerminateHigh",
  "TerminateLow",
  "TerminateOff",
  "TerminateUnknown",
  "Termination",
  "TermVRef", # DCLevels
  "TimeUnit",
  "Title", 
  "Typ",
  "U",
  "User", # DCLevels
  "Unknown",
  "V", 
  "VClamp", #DCLevels 
  "VForce", #DCLevels 
  "VICM", #DCLevels 
  "VID", #DCLevels 
  "VIH", #DCLevels 
  "VIHD", #DCLevels 
  "VIHSlew", #DCLevels 
  "VIL", #DCLevels 
  "VIHL", #DCLevels 
  "VILSlew", #DCLevels 
  "VOCM", #DCLevels 
  "VOD", #DCLevels 
  "VOH", #DCLevels 
  "VOHD", #DCLevels 
  "VOL", #DCLevels 
  "VOLD", #DCLevels 
  "Variable",
  "Vector",
  "Waveforms", 
  "WaveformTable",
  "X",
  "Z",
])


lower  = set(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'])
upper  = set(['A','B','C','D','E','F','G','H','I','j','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'])
number = set(['0','1','2','3','4','5','6','7','8','9'])
alphanumeric = set(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                    'A','B','C','D','E','F','G','H','I','j','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                    '0','1','2','3','4','5','6','7','8','9', '_'])
re_digits = re.compile("^\d+$")
spaces = set([" ","\n","\t"])
special = set([';','.','{','}','-','+','!','@','#','$','%','^','&','*',
               '(',')','=','|','`','~','[',']',':','<','>','.',',',
              '\'', # TODO: This may need to move... 
              ])
 
