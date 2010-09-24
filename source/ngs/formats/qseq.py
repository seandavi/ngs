#!/usr/bin/env python
# encoding: utf-8


import sys
import os
import unittest

def phred64ToStdqual(qualin):
    """
    Convert phred64-encoded quality string to phred33-encoding

    :param qualin: The phred64-encoded string
    :type qualin: string
    :rtype: string
    """
    return(''.join([chr(ord(x)-31) for x in qualin]))

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
            qual=phred64ToStdqual(sp[9])
        return("@%s:%s:%s:%s:%s\n%s\n+\n%s\n" % (self.machine,
                                                 self.run,
                                                 self.lane,
                                                 self.tile,
                                                 self.xcoord,
                                                 self.ycoord,
                                                 self.sequence,
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
        if(fname.endswith("gz")):
            self.fh=gzip.open(fname,"r")
        else:
            self.fh=open(fname,'r')
    
    def parse(self):
        """
        Iterate over the lines in the qseqFile, returning
        qseqRecords one-at-a-time.
        """
        for line in self.fh:
            yield(qseqRecord(line))

