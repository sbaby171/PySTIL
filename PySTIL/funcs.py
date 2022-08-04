import os
import contextlib
import gzip
import re
import references
# ----------------------------------------------------------------------------:
def report_filesize_and_processing(start,end,ln,File,debug=False):
    func = "report_filesize_and_processing"
    filesize = os.path.getsize(File)
    if int(filesize) >= 100000: filesize = filesize / 1000000.0; unit = "MB"
    else: unit = "B"
    print("DEBUG: [%s]: Processing time : %s sec."%(func,end - start)) 
    print("DEBUG: [%s]: Lines processed : %s lines."%(func,ln))
    print("DEBUG: [%s]: File-size       : %s %s."%(func,filesize,unit))
# ----------------------------------------------------------------------------:
def get_domain_name(line,kw): 
    sline = line.split()
    if sline[0] != kw: 
        raise ValueError("Beginning of line doesn't match keyword provided: "\
                         "kw = %s, line = %s"%(kw, line))
    domain = str(references.GLOBAL_DOMAIN)
    if len(sline) > 1: 
        if sline[1] != "{": 
            domain = sline[1]
    return domain 
# ----------------------------------------------------------------------------:
def _read_line(File):
    if File.endswith(".gz"):
        with contextlib.closing(gzip.open(File,'r')) as fh: 
            for ln, line in enumerate(fh,start=1): 
                yield ln, line.strip()
    else: 
        with open(File,"r") as fh: 
            for ln, line in enumerate(fh,start=1): 
                yield ln, line.strip()
# ----------------------------------------------------------------------------:
