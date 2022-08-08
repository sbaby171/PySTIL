import unittest, os, sys
sys.path.append("/nfs/causers2/msbabo/WORK/STIL/PySTIL")
import PySTIL.stil

PATH = os.path.join(os.getcwd(), "tests", "stils")
DEBUG = 0
# ============================================================================:
class TestSignalsAndSignalGroups(unittest.TestCase):
    def test_signals_1(self):
        stilfile = os.path.join(PATH,"signals.stil")
        stil = PySTIL.stil.read(stilfile)
        failed = False
        msg = []
        # --------------------------------------------------------------------:
        signals = stil.get_signals() 
        if len(signals) != 32:  
            failed = True
            msg.append("Num-of-signals should be 32. Found %s"%(len(signals)))
        #if len(signals.get_names()) != 9: 
        #    failed = True
        #    msg.append("The number of names returned should be 9.")
        #if len(signals.get_names(regex="D\d")) != 2: 
        #    failed = True
        #    msg.append("The number of names returned from regex 'D\d' should be 2.")
        #if len(signals.get_names(types=['Out'])) != 2: 
        #    failed = True
        #    msg.append("The number of names returned from types should be 2.")
        #if len(signals.get_names(regex="S0", types=['In'])) != 1: 
        #    failed = True
        #    msg.append("The number of names returned from rege='S0' and types=['In'] should be 1.")
        self.assertTrue(failed == False, "\n".join(msg))
if __name__ == "__main__": 
    unittest.main()
