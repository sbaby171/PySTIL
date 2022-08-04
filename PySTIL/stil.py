#!/usr/bin/env python
import os
import time
import re
from collections import OrderedDict
import funcs
# ----------------------------------------------------------------------------:
class STIL(object): 
    def __init__(self,*args,**kwargs): 
        pass 
# ----------------------------------------------------------------------------:
def read(stilfile,debug=False): 
    func = "PySTIL.stil.read"
    if not os.path.isfile(stilfile): 
        raise ValueError("Provide STIL file doesn't exist or has restrictive"\
           "permissions: %s"%(stilfile))
    print("DEBUG: [%s]: Received: %s"%(func,stilfile))
    TLBs = list(funcs.references.TOP_LEVEL_KEYWORDS)
    # ========================================================================:
    # (1) First Pass 
    # The first pass makes the assumption the the TOP-LEVEL block with start
    # on its own line; in that it will be the first identifier on a line. 
    # 
    # On first pass, we should becareful to only grab TOP-level blocks. This 
    # emphasis is becasue some top-level blocks can also be found within other
    # blocks. For example, the "Ann" block can be found within other blocks. 
    # 
    # Note, there are optimzations that could be made: 
    #  - popping certain TLB from search list, once they are found. 
    #  - once PatternExec block found, limit the TLB search -> if Pattern TLB
    #    only search Pattern blocks. 
    # ^^^ Much of this optmizations need to be verified, if employed, against
    #     many STILs and against the standard specifications. 
    toplevelblocks = OrderedDict() 
    toplevellines = [] # To hold all starting line keys
    stilIndex = {1:stilfile} # NOTE: Include files will add to this. 
    pass1Start = time.time()
    for ln,line in funcs._read_line(stilfile): 
        if not line: continue 
        if line.startswith("//"): continue 
        for kw in TLBs: # Moved out refs.TOP_LEVEL for optimzations
            if re.match("^%s\s|$|{"%(kw),line): 
                domain = funcs.get_domain_name(line,kw)
                if kw not in toplevelblocks: toplevelblocks[kw] = []
                toplevelblocks[kw].append({"line-count":ln, "source-file":1,"domain":domain})
                toplevellines.append(int(ln))
                if kw == "Pattern": TLBs = set(["Pattern"])
                break
    pass1End = time.time()
    funcs.report_filesize_and_processing(pass1Start,pass1End,ln,stilfile,debug=debug)
    # (1) first pass over
    for index, stil in stilIndex.items(): 
        print("%d.)  %s"%(index,stil))
    for kw,instances in toplevelblocks.items(): 
        print(kw + ": ")
        for instance in instances: 
            print("- %s"%(instance))
    print("Top-level-lines: %s"%(toplevellines))
    # NOTE: at this point, we have grabbed all the top-level tags, However, 
    # there will be false top-level tags due to references within blocks to 
    # other blocks. In some stils, I see 
    if len(toplevelblocks["PatternExec"]) > 1: 
        raise RuntimeError("Found more than 1 PatternExec block")
    lnPatternExec = toplevelblocks["PatternExec"][0]["line-count"]
    for kw, instances in toplevelblocks.items(): 
        if instances.__len__() > 1: 
            print("Multiple instances of %s"%(kw))
            for i,instance in enumerate(instances): 
                if instance["line-count"] > lnPatternExec: 
                    print("Not top-level instance: %s"%(instance))
                    del toplevelblocks[kw][i]
    for kw,instances in toplevelblocks.items(): 
        print(kw + ": ")
        for instance in instances: 
            print("- %s"%(instance))
    
    print("DEBUG: All first pass activities done")
    # ========================================================================:
    # (2) Second pass: 
    toplevelblocks["Signals"]
    for sb in toplevelblocks["Signals"]: 
        if sb["domain"] == funcs.references.GLOBAL_DOMAIN:
            start = sb["line-count"]
            end   = toplevellines[toplevellines.index(start) + 1] 
            print(start,end)
# ----------------------------------------------------------------------------:
