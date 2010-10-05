#!/usr/bin/env python
import optparse
import logging
import sys

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
    logging.basicConfig(level=10)
    logger = logging.getLogger('CGH')
    parser = optparse.OptionParser(usage="usage: %prog [options] bamfileName")
    parser.add_option('-w','--windowsize',dest='windowsize',type="int",
                      help='Windowsize for calculation of copy number')
    parser.add_option('-o','--outfile',dest='outfile',type="string",
                      help='Output filename, default <stdout>')
    parser.add_option('-l','--loglevel',dest='loglevel',type="int",
                      help='Logging Level, 1-15 with 1 being minimal logging and 15 being everything [10]')
    (opts,args) = parser.parse_args()
    if(opts.loglevel is not None):
        logger.setLevel(opts.loglevel)
    samfile = pysam.Samfile(args[0],'rb')
    lengths = samfile.lengths
    regioncounts = []
    refnames = samfile.references
    outfile=None
    if(opts.outfile is not None):
        outfile=open(opts.outfile,'w')
    else:
        outfile=sys.stdout
    totreads=0
    for ref in xrange(samfile.nreferences):
        for start in xrange(0,lengths[ref],opts.windowsize):
            c=Counter()
            samfile.fetch(refnames[ref],start,start+opts.windowsize,callback=c)
            regcount=RegionalCount(samfile.references[ref],
                                   start,start+opts.windowsize,
                                   c.mCounts)
            regioncounts.append(regcount)
            totreads+=regcount._count
            logger.info(regcount)
            outfile.write("%s\t%d\t%d\t%d\n" % (regcount.chromosome,
                                                  regcount.rbeg,
                                                  regcount.rend,
                                                  regcount._count))
    samfile.close()
    logger.info('Total Reads: %d',totreads)
    
main()
