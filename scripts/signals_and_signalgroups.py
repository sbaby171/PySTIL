import os, sys
import PySTIL.stil as pystil

debug = True
#path = """C:\Users\max.sbabo\Documents\GitHub\PySTIL\PySTIL\tests\samples\signals\signals_1.stil"""




if len(sys.argv) < 2: 
    path = os.path.join("C:\\", "Users", "max.sbabo","Documents","GitHub",
                        "PySTIL","PySTIL","tests","samples","signals","signals_1.stil")
else: 
    path = sys.argv[-1]





so = pystil.STIL(file=path, debug = debug)
so.parse() 
# ^^^ TODO: Here, we want to allow for a config file. 
# ^^^ TODO: Or, we can check a standard location and read the config file. 



siggrps  = so.get_signalgroups()
sigNames = so.get_signals()


# so.get_signals()
# - We can already imagine that the multiple parse methods are going to 
#   present issues. When using 'all' we deal directly with the tokens list
#   and the Symbol table. However, when dealing with the tplp, we are dealing 
#   first with the tplp dictionary, then moving onto to many tokens and 
#   symbolTables. 
# 
#   The second method can easily accomidate the first, that is, simply 
#   iterate over the all the entries in the tplp. 
# 
# - If many Signal blocks, only the first one should be printed.






