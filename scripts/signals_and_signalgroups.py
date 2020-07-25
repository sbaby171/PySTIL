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
    # Standard Parsing
    stil = pystil.STIL(file = args.stil, debug = args.debug)
    stil.parse()
    # Query parts

    signals = stil.get_signals()
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


    if True:
        print("\nSignalGroups:")
        siggrps  = stil.get_signalgroups()
        print(siggrps)
        # ^^^ NOTE: That here we are returning a list of sigalGroup names. 
        # This should ne questioned as to why it is different than the return 
        # on the so.get_signals(). That is because, the STIL standard only 
        # allows a signle STIL instance; whereas many SignalGroups blocks can 
        # be used in a translation. 
        GLOBAL = ' '
        instance = stil.get_signalgroups(domain = GLOBAL)
        print(instance.get_groups(signal='x[3]'))
        # TODO: or regex with 'B\[1\]'
        # TOD): also, list of regex....







