import unittest, os 
import PySTIL.stil as pystil

PATH = os.path.join(os.getcwd(), "tests", "samples", "userkeywords")
DEBUG = 0
class TestUserKeywords(unittest.TestCase):
    def test_userkeywords_1(self):
        filename = "userkeywords_1.stil"
        # Standard parsing: 
        stil = pystil.STIL(file=os.path.join(PATH, filename), debug=DEBUG)
        stil.parse()
        # Checks:  
        failed = False; msg = []
        # TODO: condense all tplp entries intoa single list. 
        #    tplp[stil.1] -> {tpl : {start,end,etc.} }
        #    tplp[stil.2] -> {tpl : {start,end,etc.} }
        #    tplp[stil.3] -> {tpl : {start,end,etc.} }
        # 
        # [tpl1s, tpl2s, tpl ]
        if 'diepad' not in stil._tplp[filename]: 
            failed = True
            msg.append("TPLP is missing 'diepad' user keyword.")
        if 'UserKeywords' not in stil._tplp[filename]: 
            failed = True
            msg.append("TPLP is missing 'UserKeywords' keyword.")
        if 'UserFunctions' not in stil._tplp[filename]: 
            failed = True
            msg.append("TPLP is missing 'UserFunctions' keyword.")
        if 'tchn' not in stil._tplp[filename]: 
            failed = True
            msg.append("TPLP is missing 'tchn' user keyword.")
        if 'abs_min' not in stil._tplp[filename]: 
            failed = True
            msg.append("TPLP is missing 'abs_min' user keyword.")

        self.assertTrue(failed == False, "\n".join(msg))
            


if __name__ == "__main__": 
    unittest.main()