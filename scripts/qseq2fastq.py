#!/usr/bin/env python
# author = sdavis
# date = 22nd May 2010
from optparse import OptionParser
import sys
import os
import re
import tarfile

def phred64ToStdqual(qualin):
    return(''.join([chr(ord(x)-31) for x in qualin]))

def outputFastq(f2,phred33=False):
    for line in f2:
        sp = line.strip().split("\t")
        qual=sp[9]
        if(phred33):
            qual=phred64ToStdqual(sp[9])
        seqString = sp[8].replace(".","N")
        print "@%s:%s:%s:%s:%s\n%s\n+\n%s" % (sp[0],sp[2],sp[3],sp[4],sp[5],seqString,qual)

usage = "usage: %prog [options] TarFileOrBustardDirectoryName"
parser = OptionParser(usage=usage)
parser.add_option("-l", "--lane", dest="lane",type='int',
                  help="The lane to convert (1-8)")
parser.add_option("-v", "--verbose", dest="verbose",
                  help="verbose, not currently used",default=False)
parser.add_option("-r", "--read",type='int',
                  dest="readNumber", default=1,
                  help="Which read to convert (1 or 2)")
parser.add_option("--phred33", action="store_true", default=False,
                  help="Convert phred scores from phred64 to phred33",dest="phred33")
parser.add_option("-t", "--tarfile", action="store_true", default=False,
                  help="Input is from a gzipped tarfile like that in the analysis sequence directory",dest="tfile")


(options, args) = parser.parse_args()
matchre = re.compile("s_%d_%d.*qseq\\.txt" % (options.lane,options.readNumber))

if(options.tfile):
    tfile = tarfile.open(args[0],"r:gz")
    for f in tfile:
        if(f.isfile()):
            f2 = tfile.extractfile(f.name)
            outputFastq(f2,options.phred33)
else:
    for i in os.listdir(args[0]):
        if(matchre.match(i)!=None):
            f2 = open(i,'r')
            outputFastq(f2,options.phred33)
            f2.close()
