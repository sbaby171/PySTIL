import os, sys
import PySTIL.stil as pystil

debug = True

if len(sys.argv) < 2: 
    path = os.path.join("C:\\", "Users", "max.sbabo","Documents","GitHub",
                        "PySTIL","PySTIL","tests","samples","signals","signals_1.stil")
else: 
    path = sys.argv[-1]





so = pystil.STIL(file=path, debug = debug)
so.parse() 
# ^^^ TODO: Here, we want to allow for a config file. 
# ^^^ TODO: Or, we can check a standard location and read the config file. 


signals = so.get_signals()
# NOTE: If this returns a single object, then get_signalGroups should return a list fo objects
print("Signal: ")
print("-------")
print(signals.string()) # NOTE: Could override the __str__ function
print("Signals.get_names()")
print("  ", signals.get_names())
print("Signal.get_names(types=[\"Out\"])")
print("  ", signals.get_names(types=["Out"]))
print("Signals.get_names(regex=\"D\d\", types[\"In\"])")
print("  ", signals.get_names(regex = "D\d", types=["In"]))


print("\nSignalGroups:")
siggrps  = so.get_signalgroups()
print(siggrps)
# ^^^ NOTE: That here we are returning a list of sigalGroup names. 
# This should ne questioned as to why it is different than the return 
# on the so.get_signals(). That is because, the STIL standard only 
# allows a signle STIL instance; whereas many SignalGroups blocks can 
# be used in a translation. 


GLOBAL = ' '
instance = so.get_signalgroups(domain = GLOBAL)
print(instance.get_groups(signal='B[1]'))
# TODO: or regex with 'B\[1\]'
# TOD): also, list of regex....





