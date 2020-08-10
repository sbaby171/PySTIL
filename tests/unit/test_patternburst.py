import unittest, os 
import PySTIL.stil as pystil

PATH = os.path.join(os.getcwd(), "tests", "samples", "patternbursts")
DEBUG = 0
class TestPatternBurst(unittest.TestCase):
    def test_patternburst_1(self):
        filename = "patternburst_1.stil"
        # Standard parsing.
        stil = pystil.STIL(file=os.path.join(PATH, filename), debug=DEBUG)
        stil.parse()
        # Check results 
        failed = False; msg = []



        if len(stil.PatternBursts()) != 1:
            failed = True
            msg.append("Expecting one block. Recieved %d"%(len(stil.PatternBursts())))
        
        actPatternBurstNames = stil.PatternBursts().names()
        expPatternBurstNames = ['"myPatternBurst"']
        if actPatternBurstNames != expPatternBurstNames: 
            failed = True
            msg.append("PatternBursts names are not correct.")


        pb = stil.PatternBursts().get(expPatternBurstNames[0])
        patternsRef    = pb.patterns()
        expPatternList = ['"Pattern1"','"Pattern2"','"Pattern3"',
                          '"Pattern4"','"Pattern5"','write_vecs','read_vecs']
        if len(patternsRef) != len(expPatternList): 
            failed = True 
            msg.append("The number of refrenced patterns (%s) "\
                "is not correct. Should be %d."%(len(patternsRef), len(expPatternList)))
        else: 
            for pat in patternsRef: 
                expPatternList.remove(pat)
            if len(expPatternList) != 0:
                failed = True
                msg.append("The patterns referenced didnt contain the following: %s"%(expPatternList))


        patLists = pb.get_PatLists() # NOTE, there can be many patLists.....
        for name, details in patLists[0].patterns.items(): 
            print(name, details )
        patsets = pb.get_PatSets() # NOTE, there can be many patLists.....
        for name, details in patsets[0].patterns.items(): 
            print(name, details)
        parallelPatLists = pb.get_ParallelPatLists() # NOTE, there can be many patLists.....
        for name, details in parallelPatLists[0].patterns.items(): 
            print(name, details) 





        #print(stil.PatternBursts().patterns())


        self.assertTrue(failed == False, "\n".join(msg))
