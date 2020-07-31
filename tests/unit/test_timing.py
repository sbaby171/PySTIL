import unittest, os 
import PySTIL.stil as pystil

PATH = os.path.join(os.getcwd(), "tests", "samples", "timing")
DEBUG = 0
class TestTiming(unittest.TestCase):
    def test_timing_1(self):
        filename = "timing_1.stil"
        # Standard parsing.
        stil = pystil.STIL(file=os.path.join(PATH, filename), debug=DEBUG)
        stil.parse()
        # Check results 
        failed = False; msg = []


        # stil.timing().get_waveformTables() 
        print(stil.timing())
        print(stil.timing().get_timing(pystil.GLOBAL))

        expectations = { "WavTbl1": {'period':"'per'",
                                     'numOfSignals': 9, 
                                    }, 
                         "WavTbl2": {'period':"'5.0ns'",
                                     'numOfSignals': 9, 
                                    },
                        }
        waveformtables = stil.timing().get_waveformtables()

        i = 0; end = len(waveformtables ) - 1
        while i <= end: 
            wvtbl = waveformtables[i]
            # WaveformTable names: 
            if wvtbl.name not in expectations: 
                failed = True
                msg.append("WaveformTable %s was not found"%(wvtbl.name))
                i+=1; continue
            expPeriod = expectations[wvtbl.name]['period']
            # Periods: 
            if expPeriod != wvtbl.period: 
                failed = True
                msg.append("WaveformTable %s periods mismatched: Actual: %s"%(wvtbl.name, wvtbl.period))
            # Number of signal definitions: 
            if len(wvtbl.signals()) != expectations[wvtbl.name]['numOfSignals']: 
                failed = True  
                msg.append("WaveformTable %s number of signals mismatched %s: Actual: %s"%(wvtbl.name,expectations[wvtbl.name]['numOfSignals'], len(wvtbl.signals())))
            i += 1
        self.assertTrue(failed == False, "\n".join(msg))
