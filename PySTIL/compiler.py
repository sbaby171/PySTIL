import os, sys, argparse, time, re
from collections import OrderedDict
#sys.path.append("/nfs/causers2/msbabo/WORK/STIL/PySTIL")
#import PySTIL.stil
import STILBlocks as SB
import STILFuncs  as SF
# ============================================================================:

# ============================================================================:
def _pass1(sf,allow_fullbreak=True,debug=False): 
    func = "PySTIL.compiler._pass1"
    if not os.path.isfile(sf): 
        raise ValueError("Provide STIL file doesn't exist or has restrictive"\
           " permissions: %s"%(sf))
    print("DEBUG: [%s]: Received: %s"%(func,sf))
    TLBs = list(SF.references.TOP_LEVEL_KEYWORDS)
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
    tlbs = OrderedDict() 
    #tlbs["PatternExec"] = [] # TODO: Add other blocks ? 
    #tlbs["Signals"] = [] # TODO: Add other blocks ? 
    #tlbs["SignalGroups"] = [] # TODO: Add other blocks ? 
    # ^^^^ NOTE: We are pre-loading some important blocks that we are 
    # expecting to check regardless of what user configures .
    tlls = [] # To hold all starting line keys
    stilIndex = {1:sf} # NOTE: Include files will add to this. TODO 
    ptS = time.time()
    fullbreak = False 
    for ln,line in SF._read_line(sf): 
        if not line: continue 
        if line.startswith("//"): continue
        if fullbreak: 
            if allow_fullbreak: ln = -1; break;
            else: fullbreak = False 
        for kw in TLBs: # Moved out refs.TOP_LEVEL for optimzations
            if re.match("^%s\s|$|{"%(kw),line): 
                domain = SF.get_domain_name(line,kw)
                if kw not in tlbs: tlbs[kw] = []
                tlbs[kw].append({"line-count":ln,
                                 "source-file":1,"domain":domain})
                tlls.append(int(ln))
                #if kw == "Pattern": TLBs = set(["Pattern"]) # NOTE
                if kw == "Pattern": 
                    if allow_fullbreak: fullbreak = True
                    else: TLBs = set(["Pattern"])
                break
    ptE = time.time()
    SF.report_filesize_and_processing(ptS,ptE,ln,sf,debug=debug)
    # (1) first pass over
    for index, stil in stilIndex.items(): 
        print("%d.)  %s"%(index,stil))
    for kw,instances in tlbs.items(): 
        print("DEBUG: [%s]: %s"%(func,kw))
        for instance in instances: 
            print("DEBUG: [%s]  - %s"%(func,instance))
    print("DEBUG: [%s]: Top-level-lines: %s"%(func,tlls))
    # -----------------------------------------------------------------------:
    # NOTE: at this point, we have grabbed all the top-level tags, However, 
    # there will be false top-level tags due to references within blocks to 
    # other blocks. In some stils, I see 
    # -----------------------------------------------------------------------: 
    # TODO: Technically, there can be multiple PatternExec blocks per STIL. 
    # so we should not fail if more than one, also, we should be more careful
    # for removing instances based after  
    #if len(tlbs["PatternExec"]) > 1: 
    #    raise RuntimeError("Found more than 1 PatternExec block")
    if tlbs["PatternExec"].__len__() >= 1: 
        lnPatternExec = tlbs["PatternExec"][0]["line-count"]
        print("\nDEBUG: [%s]: Cleaning top-level block instances"%(func))
        for kw, instances in tlbs.items(): 
            if instances.__len__() > 1: 
                #print("Multiple instances of %s"%(kw))
                for i,instance in enumerate(instances): 
                    if instance["line-count"] > lnPatternExec: 
                        #print("Not top-level instance: %s"%(instance))
                        del tlls[tlls.index(instance["line-count"])]
                        del tlbs[kw][i] # Remove instance
        print("DEBUG: [%s]: Top-level-blocks, line instances:"%(func))
        for kw,instances in tlbs.items(): # Debug show the new TLBs
            print("DEBUG: [%s]: %s"%(func,kw))
            for instance in instances: 
                print("DEBUG: [%s]  - %s"%(func,instance))
        print("DEBUG: [%s]: Top-level-lines: %s"%(func,tlls))
    else: raise RuntimeError("No Pattern Block found") # TODO: Maybe no fail
    if "PatternExec"  not in tlbs: tlbs["PatternExec"] = []
    if "Signals"      not in tlbs: tlbs["Signals"] = []
    if "SignalGroups" not in tlbs: tlbs["SignalGroups"] = []
    return tlbs, tlls 
# ============================================================================:
def read(stilfile, configfile="",debug=False):
    if not stilfile: 
        raise ValueError("Must provide STIL file.")
    # ------------------------------------------------------------------------:
    # TODO: Parse Configfile
    # config.opt1, config.opt2, etc.
    # ------------------------------------------------------------------------:
    # ------------------------------------------------------------------------:
    tlbs, tlls = _pass1(stilfile,debug=debug)
    # ------------------------------------------------------------------------:
    Stil = SB.STIL(filepath=stilfile)
    # ------------------------------------------------------------------------:
    # Parse the PatternExec block TODO: need lexer
    if tlbs["PatternExec"].__len__() >= 1: 
        lnS = tlbs["PatternExec"][0]["line-count"]
        try:    lnE = tlls[tlls.index(lnS) + 1] - 1
        except: lnE = 0
        pxlines = [line for ln,line in SF._read_line_range(stilfile,lnS, lnE)]
        pxtokens = SF.lex(pxlines) # TODO: build symbol table? 
        patternExec = SB.build_PatternExec(pxtokens)
        print(patternExec)
        Stil.patternExec = patternExec
    else: 
        raise ValueError("Multiple PatternExec blocks found. Need pointer"\
                         "for the specific one to chose.")
    # -----------------------------------------------------------------------:
    # -----------------------------------------------------------------------:
    # Parse the Signals block
    signals = None 
    if tlbs["Signals"].__len__() >= 1: 
        lnS = tlbs["Signals"][0]["line-count"]
        try:    lnE = tlls[tlls.index(lnS) + 1] - 1
        except: lnE = 0
        sglines = [line for ln,line in SF._read_line_range(stilfile,lnS,lnE)]
        sgtokens = SF.lex(sglines)
        signals = SB.build_Signals(sgtokens)
        print(signals)
        print(signals.name)
        print(signals.__len__())
        Stil.signals = signals 
    # -----------------------------------------------------------------------: 

# ============================================================================:
def _handle_cmd_args(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug",action="store_true", help="debug logging.")
    parser.add_argument("--stil", type=str, help="STIL file.")
    parser.add_argument("--config", type=str, help="config file.")
    args = parser.parse_args()
    return args
# ============================================================================:
if __name__ == "__main__": 
    args = _handle_cmd_args()
    read(args.stil,args.config)
    
