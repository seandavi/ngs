"""
A module for opening and parsing a VCF format file and encapsulating VCF records

The Variant Call Format (VCF) is described `here <http://1000genomes.org/wiki/doku.php?id=1000_genomes:analysis:vcf4.0>`
"""

__docformat__ = 'restructuredtext'

import gzip


class vcfFile:
    
    def __init__(self,fname):
        self.fname=fname
        self.open()

    def parse(self):
        for line in self.fh:
            (yield vcfRecord(line.strip()))

    def close(self):
        self.is_open=False
        self.fh.close()

    def open(self):
        if(self.fname.endswith('.gz')):
            self.fh=gzip.open(self.fname,'r')
        else:
            self.fh=open(self.fname,'r')
        self.is_open=True
        self.header=[]
        line=self.fh.readline()
        while(line.startswith("#")):
            self.header.append(line.strip())
            line=self.fh.readline()
        tableHeaders=self.header[-1]
        self.sampleNames=tableHeaders.split("\t")[9:]

class vcfRecord:
    def __init__(self,line):
        parts=line.split()
        self.chromosome=parts[0]
        self.position=int(parts[1])
        self.rbeg=self.position-1
        self.rend=self.position
        self.name=parts[2]
        self.ref=parts[3]
        self.alt=parts[4]
        self.qual=float(parts[5])
        self.filt=parts[6]
        self.info=parts[7]
        self.form=parts[8]
        self.samples=parts[9:]

