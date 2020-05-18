import unittest, os 

from PySTIL import stil


PATH = os.path.join(os.getcwd(), "tests", "samples", "headers")
DEBUG = 0
class TestHeaderParsingMethods(unittest.TestCase):
    def test_header_1(self):
        _file = os.path.join(PATH, "header_1.stil")
        so = stil.STIL(sfp=_file, debug=DEBUG)
        so.parse()
        self.assertTrue(so.header.get_title() == "Sample STIL Title")
        self.assertTrue(so.header.get_date() == "Tue Apr 28 12:23:48 EST 1996")
        self.assertTrue(so.header.get_source() == "VHDL simulation on April 22, 1996")
        for i, ann in enumerate(so.header.get_history()): 
            if i == 0: self.assertTrue(ann == "rev1 - 4/21/96 - made some change")
            if i == 1: self.assertTrue(ann == "rev2- 4/22/96 - made it work")

    def test_header_2(self):
        _file = os.path.join(PATH, "header_2.stil")
        so = stil.STIL(sfp=_file, debug=DEBUG)
        so.parse()
        self.assertTrue(so.header.get_title() == "Sample STIL Title")
        self.assertTrue(so.header.get_date() == "Tue Apr 28 12:23:48 EST 1996")
        self.assertTrue(so.header.get_source() == "VHDL simulation on April 22, 1996")
        for i, ann in enumerate(so.header.get_history()): 
            if i == 0: self.assertTrue(ann == "rev1 - 4/21/96 - made some change")
            if i == 1: self.assertTrue(ann == "rev2- 4/22/96 - made it work")

if __name__ == "__main__": 
    unittest.main()