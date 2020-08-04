import os, sys, argparse
import PySTIL.stil as pystil

import timeit

def _handle_cmd_args(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Increase console logging", action="store_true")
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
