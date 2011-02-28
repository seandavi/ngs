#!/usr/bin/env python
# author = sdavis
# date = 22nd May 2010
from optparse import OptionParser
import sys
import os
import re
import tarfile
import ngs.formats.qseq
import gzip

def phred64ToStdqual(qualin):
    return(''.join([chr(ord(x)-31) for x in qualin]))

def outputFastq(f2,outfile,phred33=False):
    for line in f2:
        sp = line.strip().split("\t")
        qual=sp[9]
        if(phred33):
            qual=ngs.formats.qseq.phred64ToStdqual(sp[9])
        seqString = sp[8].replace(".","N")
        outfile.write("@%s:%s:%s:%s:%s\n%s\n+\n%s\n" % (sp[0],sp[2],sp[3],sp[4],sp[5],seqString,qual))

def fileTypes(fnameList):
    """
    Returns a dict with True for each file type found:

    ret={"qseq":False,
         "seqprb":False,
         "seqprbgz":False}
    if the tile type is found, the dict entry will be set to True
    """
    matchqseq=re.compile(".*qseq\\.txt")
    matchseqprb=re.compile(".*seq\\.txt")
    matchseqprbgz=re.compile(".*seq\\.txt\\.gz")
    ret={"qseq":False,
         "seqprb":False,
         "seqprbgz":False}
    for i in fnameList:
        if(matchqseq.match(i)!=None):
            ret["qseq"]=True
        if(matchseqprb.match(i)!=None):
            ret["seqprb"]=True
        if(matchseqprbgz.match(i)!=None):
            ret["seqprbgz"]=True
    return(ret)

def tarFileExtractor(options,fname):
    tfile = tarfile.open(args[0],"r:gz")
    fileList=[f.name for f in tfile]
    ftypes=fileTypes(fileList)
    if(ftypes['qseq']==True):
        for f in tfile:
            if(f.isfile()):
                f2 = tfile.extractfile(f.name)
                outputFastq(f2,outfile,options.phred33)
        return
    if(ftypes['seqprb'] | ftypes['seqprbgz']):
        for fname in fileList:
            if(fname.endswith("seq.txt") | fname.endswith("seq.txt.gz")):
                seqfile=tfile.extractfile(fname)
                prbfile=tfile.extractfile(fname.replace('seq','prb'))
                seqprbParser=ngs.formats.qseq.seqprbFile(fhs=(seqfile,prbfile))
                if(options.split is not None):
                    for fq in seqprbParser.parse():
                        outfile.write(fq + "\n")
                else:
                    for fq in seqprbParser.parse():
                        outfile.write(fq[1] + "\n")
        return

usage = """%prog [options] TarFileOrBustardDirectoryName

This little script takes qseq or seq/prb archives and 
converts to fastq format.  The files can be in a tar.gz 
archive or simply in a directory and can be compressed 
or not within the tarfile or directory."""
parser = OptionParser(usage=usage)
parser.add_option("-l", "--lane", dest="lane",type='int',
                  help="The lane to convert (1-8)")
parser.add_option("-v", "--verbose", dest="verbose",
                  help="verbose, not currently used",default=False)
parser.add_option("-r", "--read",type='int',
                  dest="readNumber", default=1,
                  help="Which read to convert (1 or 2)")
parser.add_option("--phred33", action="store_true", default=True,
                  help="Convert phred scores from phred64 to phred33",dest="phred33")
parser.add_option("-t", "--tarfile", action="store_true", default=False,
                  help="Input is from a gzipped tarfile like that in the analysis sequence directory",dest="tfile")
parser.add_option("-o","--outfile",dest="outfile",default=None,
                  help="Output file name")
parser.add_option("-w","--overwrite",dest="overwrite",action="store_true",
                  default=False,help="Overwrite existing file with same name")
parser.add_option("-s","--split-seqprb",dest="split",default=None,
                  help="""For seq/prb files, multiple reads are stored in a single pair of files.  Specify a split value (1-based) representing the last base of the first read (80 for paired 80mers, for example)""")



(options, args) = parser.parse_args()
matchre=re.compile("s_.*qseq\\.txt")
if((options.readNumber is not None) & (options.lane is not None)):
    matchre = re.compile("s_%d_%d.*qseq\\.txt" % (options.lane,options.readNumber))
elif((options.readNumber is not None)):
    matchre = re.compile("s_.*_%d.*qseq\\.txt" % (options.readNumber))
elif((options.lane is not None)):
    matchre = re.compile("s_%d_.*.*qseq\\.txt" % (options.lane))

outfile=sys.stdout
if(options.outfile is not None):
    if((os.path.exists(options.outfile)) & (~options.overwrite)):
        exit(0)
    if(options.outfile.endswith('gz')):
        outfile=gzip.open(options.outfile,'wb')
    else:
        outfile=open(options.outfile,'w')
if(options.tfile):
    tarFileExtractor(options,args[0])
else:
    for i in os.listdir(args[0]):
        if(matchre.match(i)!=None):
            f2 = open(i,'r')
            outputFastq(f2,outfile,options.phred33)
            f2.close()
