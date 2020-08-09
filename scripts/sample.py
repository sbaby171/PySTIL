import os, sys, argparse
import PySTIL.stil as pystil

import timeit

def _handle_cmd_args(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Increase console logging", action="store_true")
    parser.add_argument("--Timings", help="Dump Timing findings", action="store_true")
    parser.add_argument("--PatternBursts", help="Dump PatternBurst findings", action="store_true")
    parser.add_argument("--Specs", help="Dump Speec findings", action="store_true")
    parser.add_argument("--all", help="Tokenize entire STIL", action="store_true")
    parser.add_argument("stil", help="STIL file path",)
    args = parser.parse_args()
    if not os.path.isfile(args.stil): 
        raise ValueError("Invalid STIL file.")
    return args

if __name__ == "__main__":
    args = _handle_cmd_args()
    # Standard Parsing
    stil = pystil.STIL(file = args.stil, debug = args.debug)

    # TODO: Need 'best' way to time the function. 
    #https://stackoverflow.com/questions/7370801/how-to-measure-elapsed-time-in-python?page=1&tab=active#tab-top
    start = timeit.timeit()
    stil.parse()
    end = timeit.timeit()
    print("Execution time: %s"%(end-start))
    
    #print(stil._tplp)
    stil.print_tplp() 

    # Timing: 
    # ---------------------: 
    if args.Timings: 
        print("Timings: ")
        print("=======:")
        timings = stil.Timings()
        print("Timing Domains: %s"%(timings.names()))
        print("Timing Wavetables:")
        for wvtbl in timings.WaveformTables(): 
            print("  - %s"%(wvtbl.name))
        print("")

    # Spec: 
    # ------------: 
    if args.Specs: 
        print("Specs: ")
        print("=============:")
        print("Domains: %s"%(stil.Specs().names()))
        print("Categories: %s"%(stil.Specs().Categories()))

    # PatternBurst: 
    # ------------: 
    if args.PatternBursts: 
        print("PatternBursts: ")
        print("=============:")
        print("Domains: %s"%(stil.PatternBursts().names()))
        pb = stil.PatternBursts().get("\"b_ga106_a01_iobist_pll_fb_htol_p2G_1p35_hssa_dp_cont_dqdata_prbs_IN_D15_d_4\"")
        print("Patterns Referenced:")
        for pat in pb.patterns(): 
            print(" - %s"%(pat))
        print("")
    


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
