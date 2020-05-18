import unittest, os 

from PySTIL import stil


PATH = os.path.join(os.getcwd(), "tests", "samples", "signals")
DEBUG = 0
class TestHeaderParsingMethods(unittest.TestCase):
    def test_signals_1(self):
        _file = os.path.join(PATH, "signals_1.stil")
        so = stil.STIL(sfp=_file, debug=DEBUG)
        so.parse()
        self.assertTrue(len(so.signals) == 16)


        signalNameAnswers = ["CP", "MR", "S0", "S1", "D0", "D7", "Q0", "Q7", 
                             "IO[0]", "IO[1]","IO[2]","IO[3]","IO[4]","IO[5]","IO[6]","IO[7]"]
        failed = False 
        for signal in so.signals: 
            if signal.name not in signalNameAnswers:  
                failed = True
        self.assertTrue(failed == False, "The signal names are not matching")



if __name__ == "__main__": 
    unittest.main()