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


        print(stil._tplp)