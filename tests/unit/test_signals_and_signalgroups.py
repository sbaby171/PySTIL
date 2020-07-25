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
        self.assertTrue(failed == False, "\n".join(msg))

    def test_signals_2(self):
        filename = "signals_2.stil"
        # Standard parsing.
        stil = pystil.STIL(file=os.path.join(PATH, filename), debug=DEBUG)
        stil.parse()
        # Check results 
        failed = False; msg = []

        # Check number of signals defined: 
        signals = stil.signals()

        numOfSignals = 26
        if signals.get_size() != numOfSignals:  
            failed = True
            msg.append("The number of channels should be %s; %s found."%(numOfSignals, signals.get_size()))

        signalGroups = stil.get_signalgroups()
        #signalGroups = stil.signalGroups() # This will return a list. 
        # however we want an object interface. 
        # NOTE: Never have multiple return types!
        # This makes maintainance tooo complicated. 
        #signalGroups = stil.signalGroups() # TODO: Return SignalGroupBlocks
        #signalGroups.get_groups() # TODO: Return list of 
        



        # NOTE: A list is returned here! Signals is different than nearily
        # all other block returns because stil standard only accepts one.
        # That is stil ignores all Signal blocks after the first one.


        domains = stil.signalGroups().get_domains()
        numOfDomains = 2
        if len(domains) != numOfDomains: 
            failed = True
            msg.append("The number of domains should be %s; %s found."%(numOfDomains, stil.signalGroups().get_domains()))
        
        blockX = stil.signalGroups().get_block(domain = " ")
        groups = blockX.get_groups(signal="B[1]")
        if len(groups) != 2: 
           failed = True
           msg.append("The number of groups  should be %s when search for B[1]; %s found."%(2, len(groups)))
        if groups[0] != 'bbus_pins': 
           failed = True
           msg.append("The groups[0] = %s, should be %s found."%(groups[0], 'bbus_pins'))
        if groups[1] != 'bbus_odd': 
           failed = True
           msg.append("The groups[1] = %s, should be %s found."%(groups[1], 'bbus_odd'))
        groups = blockX.get_groups()
        if len(groups) != 5: 
           failed = True
           msg.append("The number of groups should be %s. %s found."%(5, len(groups)))
        groups = blockX.get_groups(signal="scan1")
        if len(groups) != 1: 
           failed = True
           msg.append("The number of groups should be %s when search for 'scan1'; %s found."%(1, len(groups)))
        groups = stil.signalGroups().get_block(domain="quality").get_groups()
        if len(groups) != 3: 
           failed = True
           msg.append("The number of groups should be %s. %s found."%(3, len(groups)))
 
        







        self.assertTrue(failed == False, "\n".join(msg))



            
if __name__ == "__main__": 
    unittest.main()