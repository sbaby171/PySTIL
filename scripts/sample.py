import os, sys, argparse
import PySTIL.stil as pystil

import timeit

def _handle_cmd_args(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Increase console logging", action="store_true")
    parser.add_argument("--Timings", help="Dump Timing findings", action="store_true")
    parser.add_argument("--PatternBursts", help="Dump PatternBurst findings", action="store_true")
    parser.add_argument("--Specs", help="Dump Spec findings", action="store_true")
    parser.add_argument("--SignalGroups", help="Dump SignalGroups findings", action="store_true")
    parser.add_argument("--all", help="Tokenize entire STIL", action="store_true")
    parser.add_argument("stil", help="STIL file path",)
    args = parser.parse_args()
    if not os.path.isfile(args.stil): 
        raise ValueError("Invalid STIL file.")
    return args

if __name__ == "__main__":
    args = _handle_cmd_args()

    # Various constructors: 
    stil = pystil.STIL(readpath = args.stil, debug = args.debug) 
 
    # Reading: 
    # --------
    # Can also provide readpath here, 
    # iff not already set.
    stil.read() 
    stil.print_tplp()

    # Writing: 
    #stil.write()
    # This will write STIL file(s).  


    # Includes: 
    # --------: 
    hasIncludes = False 
    print("\nIncludes:")
    print("========:")
    if stil.has_Includes():
        hasIncludes= True
        includes = stil.Includes()
        for entry in includes: 
            print("Base file: %s"%(entry))
            for instance in includes[entry]: 
                print("  - %s"%(instance))
    else: print("This STIL instance contains no 'Include'.")



    # SignalGroups: 
    # ------------: 
    if args.SignalGroups: 
        print("\nSignalGroups: ")
        print("=============:")
        signalGroupsBlocks = stil.SignalGroups()
        print("SignalGroups Name Blocks (domains):")
        domains = signalGroupsBlocks.names()
        for domain in domains: 
            print("  - %s,  file: %s"%(domain, signalGroupsBlocks.get(domain).get_file()))
        print("")

    # PatternBurst: 
    # ------------: 
    if args.PatternBursts: 
        print("\nPatternBursts: ")
        print("=============:")
        patternBurstBlocks = stil.PatternBursts()
        print("PatternBurst Name Blocks (domains):")
        domains = patternBurstBlocks.names()
        for domain in domains: 
            print("  - %s,  file: %s"%(domain, patternBurstBlocks.get(domain).get_file()))
        print("")
        pb = stil.PatternBursts().get(domains[0])
        print("Patterns Referenced in %s:"%(domains[0]))
        for pat in pb.patterns(): 
            print(" - %s"%(pat))
        print("")


    # Timing: 
    # ---------------------: 
    if args.Timings: 
        print("\nTimings: ")
        print("=======:")
        timingBlocks = stil.Timings()

        print("Timing Name Blocks (domains):")
        domains = timingBlocks.names()
        for domain in domains: 
            print("  - %s, file: %s"%(domain, timingBlocks.get(domain).get_file()))
        print("")

        print("Timing Wavetables:")
        for wvtbl in timingBlocks.WaveformTables(): 
            print("  - %s"%(wvtbl.name))
        print("")

    # Spec: 
    # ------------: 
    # TODO: nv-028 seeing instance of multiple variable instance within Spec/Category. 
    if args.Specs: 
        print("\nSpecs: ")
        print("=============:")
        specs = stil.Specs()
        print("Spec Name Blocks (domains):")
        domains = specs.names()
        for domain in domains: 
            print("  - %s,  file: %s"%(domain, specs.get(domain).get_file()))
        print("Categories: %s"%(stil.Specs().Categories()))







    # Query parts

    # Timing: 
    #stil.timing()


    # UserKeywords: 
    #userkeyword = "CustomExpansion"
    #instances = stil.get_userkeyword("CustomExpansion")
    #print(instances)
    #
    #for instance in instances: 
    #    tokens = pystil.sutils.lex(instance)
    #    #print(tokens)
