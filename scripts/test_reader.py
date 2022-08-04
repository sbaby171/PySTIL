#!/usr/bin/env python
# ----------------------------------------------------------------------------:
import os, sys, argparse
sys.path.append("/nfs/causers2/msbabo/WORK/STIL/PySTIL")
import PySTIL.stil
# ----------------------------------------------------------------------------:
def handle_cmd_args(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug",
                        action="store_true",
                        help="increase output logging.")
    parser.add_argument("--stil",
                        type=str, 
                        help="STIL file.")
    args = parser.parse_args()
    return args
# ----------------------------------------------------------------------------:
args = handle_cmd_args()
if not args.stil: 
    raise ValueError("Must provide STIL file.")
PySTIL.stil.read(args.stil)
