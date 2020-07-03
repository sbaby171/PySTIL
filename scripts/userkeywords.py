import os, sys, argparse
import PySTIL.stil as pystil



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
    stil = pystil.STIL(file = args.stil, debug = args.debug)
    stil.parse()


    userkeyword = "CustomExpansion"
    instances = stil.get_userkeyword("CustomExpansion")
    for instance in instances: 
        tokens = pystil.sutils.lex(instance)
        #print(tokens)

    
