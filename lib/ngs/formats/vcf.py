"""
A module for opening and parsing a VCF format file and encapsulating VCF records

The Variant Call Format (VCF) is described `here <http://1000genomes.org/wiki/doku.php?id=1000_genomes:analysis:vcf4.0>`
"""

__docformat__ = 'restructuredtext'

import gzip
import re

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
        while(not (line.startswith("#CHROM"))):
            self.header.append(line.strip())
            line=self.fh.readline()
        self.header.append(line.strip())
        tableHeaders=self.header[-1]
        self.sampleNames=tableHeaders.split("\t")[9:]
        self.header=self._parseHeader(self.header)

    def _parseHeader(self,header):
        headerstuff={}
        infolines=[re.sub("##INFO=<","",line) for line in header \
                   if line.startswith("##INFO")]
        infolines=[re.sub(">$","",line) for line in infolines]
        headerInfo=[]
        for line in infolines:
            print line
            headerInfo.append(dict([member.split("=",1) \
                               for member in line.split(",",3)]))
        headerstuff['INFO']=headerInfo
        return(headerstuff)

class vcfRecord:
    def __init__(self,line):
        parts=line.split()
        self.chromosome=parts[0]
        self.position=int(parts[1])
        self.rbeg=self.position-1
        self.rend=self.position
        self.name=parts[2]
        self.refAllele=parts[3]
        self.altAlleles=parts[4].split(",")
        self.quality=float(parts[5])
        self.filt=parts[6]
        self.info=parts[7].split(";")
        self.samples=[dict(zip(parts[8].split(":"),y.split(":"))) for y in parts[9:]]

