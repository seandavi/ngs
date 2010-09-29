#!/usr/bin/env python
import optparse
import logging

import pysam
import ngs.regions

class Counter:
    mCounts = 0
    def __call__(self, alignment):
        self.mCounts += 1

class RegionalCount(ngs.regions.Region):
    def __init__(self,chromosome,rbeg,rend,count):
        ngs.regions.Region.__init__(self,chromosome,rbeg,rend)
        self._count=count

    def __str__(self):
        return("%s:%d-%d <%d>" % (self.chromosome,self.rbeg,self.rend,self._count))

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('CGH')
    parser = optparse.OptionParser(usage="usage: %prog [options] bamfileName")
    parser.add_option('-w','--windowsize',dest='windowsize',type="int",
                      help='Windowsize for calculation of copy number')
    (opts,args) = parser.parse_args()
    samfile = pysam.Samfile(args[0],'rb')
    lengths = samfile.lengths
    regioncounts = []
    refnames = samfile.references
    for ref in xrange(samfile.nreferences):
        for start in xrange(0,lengths[ref],opts.windowsize):
            c=Counter()
            samfile.fetch(refnames[ref],start,start+opts.windowsize,callback=c)
            regcount=RegionalCount(samfile.references[ref],
                                   start,start+opts.windowsize,
                                   c.mCounts)
            regioncounts.append(regcount)
            logger.info(regcount)
    samfile.close()

main()
