import unittest, os 
import PySTIL.stil as pystil

PATH = os.path.join(os.getcwd(), "tests", "samples", "signals")
DEBUG = 0
class TestSignalsAndSignalGroups(unittest.TestCase):
    def test_signals_1(self):
        filename = "signals_1.stil"
        # Standard parsing.
        stil = pystil.STIL(file=os.path.join(PATH, filename), debug=DEBUG)
        stil.parse()
        # Check results 
        failed = False; msg = []

        # Check number of signals, 
        #   - Technically, 16 signal defintions. IO[0..7] is more 8 channels. 
        #     This acknowledges that we need to be able to reference multiple
        #     variations of shorthand notation 
        # TODO: Does this shorthand notation allow for subset references? 
        #   ex.) "a&b"[0..7], is the following references valid? 
        #    - "a&b"[0..2] -> "a&b"[0] "a&b"[1] "a&b"[2]
        #    - "a&b"[6..4] -> "a&b"[6] "a&b"[5] "a&b"[4]

        signals = stil.get_signals() 

        if signals.get_size() != 16:  
            failed = True
            msg.append("The number of channels should be 16.")
        if len(signals.get_names()) != 9: 
            failed = True
            msg.append("The number of names returned should be 9.")
        if len(signals.get_names(regex="D\d")) != 2: 
            failed = True
            msg.append("The number of names returned from regex 'D\d' should be 2.")
        if len(signals.get_names(types=['Out'])) != 2: 
            failed = True
            msg.append("The number of names returned from types should be 2.")
        if len(signals.get_names(regex="S0", types=['In'])) != 1: 
            failed = True
            msg.append("The number of names returned from rege='S0' and types=['In'] should be 1.")

        #print("Signal.get_names(types=[\"Out\"])")
        #print("  ", signals.get_names(types=["Out"]))
        #print("Signals.get_names(regex=\"D\d\", types[\"In\"])")
        #print("  ", signals.get_names(regex = "D\d", types=["In"]))
        self.assertTrue(failed == False, "\n".join(msg))
            

            
if __name__ == "__main__": 
    unittest.main()