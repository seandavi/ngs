#!/usr/bin/env python
# encoding: utf-8

import string
import sys
import os
import unittest
import gzip
import itertools
from math import log

## fast conversion from phred-64 to phred-33
_trans = string.maketrans(''.join(chr(i) for i in range(31, 127)), ''.join(chr(i) for i in range(127 - 31)))

## This is for converting pre-1.3 qualities to std qualities
## taken from fq_all2std.pl
conv_table={}
for x in range(-64,65):
    conv_table[x+64] = int(33 + 10*log(1+10**(x/10.0))/log(10)+.499)

def generalFileOpen(fname,mode='r'):
    if(fname.endswith("gz")):
        return(gzip.open(fname,mode))
    else:
        return(open(fname,mode))

def phred64ToStdqual(qualin):
    """
    Convert phred64-encoded quality string to phred33-encoding

    :param qualin: The phred64-encoded string
    :type qualin: string
    :rtype: string
    """
    return qualin.translate(_trans)

class qseqRecord:
    """Encapsulate a qseqRecord.

    A qseq record is usually phred-64 encoded, so it may be necessary
    to convert to phred-33 for downstream use.  To create a new record,
    pass in the line from the qseq file.

    The fields are encoded like this::
    
        fields=line.strip().split("\t")
        self.machine=fields[0]
        self.run=fields[1]
        self.lane=int(fields[2])
        self.tile=int(fields[3])
        self.xcoord=int(fields[4])
        self.ycoord=int(fields[5])
        self.indexnum=int(fields[6])
        self.read=int(fields[7])
        self.sequence=fields[8]
        self.quality=fields[9]
        self.filter=bool(fields[10])
        
    """
    
    def __init__(self,line):
        """Create a new qseqRecord from a single string representing
        the qseq line"""
        fields=line.strip().split("\t")
        self.machine=fields[0]
        self.run=fields[1]
        self.lane=int(fields[2])
        self.tile=int(fields[3])
        self.xcoord=int(fields[4])
        self.ycoord=int(fields[5])
        self.indexnum=int(fields[6])
        self.read=int(fields[7])
        self.sequence=fields[8]
        self.quality=fields[9]
        self.filter=bool(fields[10])

    def __str__(self):
        """
        Return a properly-formated qseq line
        """
        return "%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s\t%d" % (self.machine,self.run,self.lane,self.tile,
                          self.xcoord,self.ycoord,self.indexnum,
                          self.read,self.sequence,self.quality,
                          self.filter)
    def asFastqString(self,phred33=True):
        """
        Return the qseq record as a fastq string

        :param phred33: Convert to phred33-scaled qualities before returning
        :type phred33: Boolean
        :rtype: string representing fastq record

        .. todo::

            Should return a fastq record at some point
        """
        qual=self.quality
        if(phred33):
            qual=phred64ToStdqual(self.quality)
        return("@%s:%s:%d:%d:%d:%d\n%s\n+\n%s\n" % (self.machine,
                                                 self.run,
                                                 self.lane,
                                                 self.tile,
                                                 self.xcoord,
                                                 self.ycoord,
                                                 self.sequence.replace(".","N"),
                                                 qual))

class qseqFile:
    """
    Create a new qseqFile

    Takes either a fname or a filehandle.  If filehandle is
    given, it is used directly.  Otherwise, the filename
    is parsed and if it ends in .gz, the file is opened as a
    gzipped file.

    :param fname: A filename, may end in .gz in which case, assumed to be a gzipped file
    :param fh: A file handle of an already opened file
    :rtype: An object of type :class:`qseqFile`

    Usage is along the lines of::
    
        x = qseq.qseqFile(fname='../../../testdata/s_1_1_0005_qseq.txt')
        for qseqrecord in x.parse():
            print qseqrecord
    """
    def __init__(self,fname=None,fh=None):
        """
        Create a new qseqFile

        Takes either a fname or a filehandle.  If filehandle is
        given, it is used directly.  Otherwise, the filename
        is parsed and if it ends in .gz, the file is opened as a
        gzipped file.

        :param fname: A filename, may end in .gz in which case, assumed to be
        a gzipped file
        :param fh: A file handle of an already opened file
        :rtype: An object of type :class:`qseqFile`
        """
        if(fh is not None):
            self.fh=fh
            return
        self.fh=generalFileOpen(fname,"r")
    
    def parse(self):
        """
        Iterate over the lines in the qseqFile, returning
        qseqRecords one-at-a-time.
        """
        for line in self.fh:
            yield(qseqRecord(line))

class seqprbFile:
    """
    Encapsulates a pair of files, the _seq.txt and _prb.txt files from Illumina

    usage is along the lines of:

    >>> import ngs.formats.qseq
    >>> spfile = ngs.formats.qseq.seqprbFile(filenames=("s_1_0033_seq.txt","s_1_0033_prb.txt"))
    >>> for i in spfile.parse():
    >>>     print i

    This will return a phred-33 quality fastq string
    """
    def __init__(self,filenames=None,fhs=None):
        # takes a tuple of either two filenames or two file handles.
        # The first is the seq file and the second is prb.
        if(fhs is not None):
            ### Even the files within the tarfile might be gzipped
            if(fhs[0].name.endswith(".gz")):
                self._seqfile=gzip.GzipFile(mode='r',fileobj=fhs[0])
            else:
                self._seqfile=fhs[0]
            if(fhs[2].name.endswith(".gz")):
                self._prbfile=gzip.GzipFile(mode='r',fileobj=fhs[1])
            else:
                self._prbfile=fhs[1]
        else:
            self._seqfile=generalFileOpen(filenames[0],'r')
            self._prbfile=generalFileOpen(filenames[1],'r')

    def parse(self,split):
        """
        Parse a seq/prb file pair into fastq chunks.

        :param split: If the seq/prb pair represents a paired-end read, return a tuple of two fastq strings by splitting the read and quality at split.
        :type split: integer
        :rtype: either a string or tuple of strings (if split split is supplied) representing fastq records
        """
        for seq,prb in itertools.izip(self._seqfile,self._prbfile):
            seqsplit = seq.strip().split()
            seqname = ":".join(seqsplit[0:4])
            seqseq  = seqsplit[4].replace('.','N')
            prbsplit = [int(x) for x in prb.strip().split()]
            qual = []
            for j in xrange(0,len(prbsplit),4):
                qual.append(chr(conv_table[max(prbsplit[j:(j+4)])+64]))
            qualstring = "".join(qual)
            if(split==None):
                yield("@%s\n%s\n+%s\n%s" % (seqname,seqseq,seqname,"".join(qual)))
            else:
                yield(("@%s\n%s\n+%s\n%s" %
                      (seqname,seqseq[0:(split+1)],
                       seqname,qualstring[0:(split+1)]),
                       "@%s\n%s\n+%s\n%s" %
                      (seqname,seqseq[(split+1):],
                       seqname,qualstring[(split+1):])))

