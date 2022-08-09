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
        signals = stil.get_Signals() 
        if len(signals) != 50:  
            failed = True
            msg.append("Num-of-signals should be 50. Found %s"%(len(signals)))
        # --------------------------------------------------------------------:
        signalGroups = stil.get_SignalGroups()
        if len(signalGroups) != 3: 
            failed = True
            msg.append("Num-of-signalsGroups should be 3. Found %s"%(len(signalGroups)))

        self.assertTrue(failed == False, "\n".join(msg))
if __name__ == "__main__": 
    unittest.main()
