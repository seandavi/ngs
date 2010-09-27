#!/usr/bin/env python
import pysam
import optparse
import collections
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReadDistributions")

def calculateReadDistributions(bamfilename):
    readlens = collections.defaultdict(int)
    isizes = collections.defaultdict(int)
    f = pysam.Samfile(args[0],'rb')
    k = 0
    for alignedRead in f.fetch():
        k+=1
        if((k % 1000000)==0):
            logger.info("%d records processed" % (k))
        if(alignedRead.is_read1 & alignedRead.is_paired):
            readlens[len(alignedRead.qual)]+=1
            isizes[abs(alignedRead.isize)]+=1
    f.close()
    return(readlens,isizes)

def main(bamfilename):
    (readlens,isizes) = calculateReadDistributions(bamfilename)
    fbase = os.path.splitext(args[0])[0]
    outfile = open(fbase + ".readLengthHisto",'w')
    outfile.write("[ReadLengths]\n")
    outfile.write("Length\tCount\n")
    for key in sorted(readlens.keys()):
        outfile.write("%d\t%d\n" % (key,readlens[key]))
    outfile.write("[InsertSizes]\n")
    outfile.write("InsertSize\tCount\n")
    for key in sorted(isizes.keys()):
        outfile.write("%d\t%d\n" % (key,isizes[key]))
    outfile.close()

if __name__=="__main__":
    parser=optparse.OptionParser(usage="""usage: %prog sortedBamFilename""")
    (opts,args)=parser.parse_args()
    if(len(args)<>1):
        parser.error("Must specify bamfile name")
    main(args[0])
