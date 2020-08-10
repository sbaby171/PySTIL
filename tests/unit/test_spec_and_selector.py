import unittest, os 
import PySTIL.stil as pystil

PATH = os.path.join(os.getcwd(), "tests", "samples", "spec")
DEBUG = 0
class TestSpecAndSelector(unittest.TestCase):
    def test_spec_1(self):
        filename = "spec_1.stil"
        # Standard parsing.
        stil = pystil.STIL(file=os.path.join(PATH, filename), debug=DEBUG)
        stil.parse()
        # Check results 
        failed = False; msg = []


        #print(stil._tplp)
        #print(stil.specs())
        
        # NOTE: The question is how will user typically reference the 
        # category blocks.
        if len(stil.Specs()) != 1:
            failed = True
            msg.append("Expecting one block. Recieved %d"%(len(stil.Specs())))

        spec = stil.Specs().get(name="tmode_spec")
        categories = spec.get_categories()

        if len(categories) != 2:
            failed = True
            msg.append("Expecting 2 categories. Recieved %d"%(len(categories)))

        tmodeCat = spec.category("tmode")
        if (len(tmodeCat) != 7): 
            failed = True
            msg.append("Expecting 7 categories. Recieved %d"%(len(tmodeCat)))

        if tmodeCat.vars["dutyb"] != {'value': "'0.00ns'"}: 
            failed = True
            msg.append("Dictionary for tmode's 'dutyb' is not proper.")

        tmodeSlow = spec.category("tmode_slow")
        if (len(tmodeSlow) != 7): 
            failed = True
            msg.append("Expecting 7 categories. Recieved %d"%(len(tmodeCat)))

        if tmodeSlow.vars["shmsp5"] != {'Min':"'0.00ns'",'Typ':"'23.00ns'",'Max':"'40.00ns'"}:
            failed = True
            msg.append("Dictionary for tmode_slow's 'shmsp5' is not proper.")

        if len(stil.selectors()) != 2: 
            failed = True
            msg.append("Expecting 2 Selector. Recieved %s"%(len(stil.selectors())))

        if stil.selectors().selector("tmode_typ").vars["sp5"] != 'Typ':
            failed = True
            msg.append("Expecting 'tmode_typ' 'sp5' to be 'Typ'.")

        if stil.selectors().selector("tmode_mix").vars["shmsp5"] != 'Max':
            failed = True
            msg.append("Expecting 'tmode_mix' 'shmsp5' to be 'Max'.")

        self.assertTrue(failed == False, "\n".join(msg))

        