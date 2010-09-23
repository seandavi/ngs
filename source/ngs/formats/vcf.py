"""
A module for opening and parsing a VCF format file and encapsulating VCF records

The Variant Call Format (VCF) is described `here <http://1000genomes.org/wiki/doku.php?id=1000_genomes:analysis:vcf4.0>`
"""

__docformat__ = 'restructuredtext'

import gzip
import re

class vcfHeader(dict):
    """
    Contains the header tag lines from a VCF file

    Currently, this class simply stores three dicts, INFO, FORMAT, and FILTER.
    Each of these dicts contains a dict of tags and potentially many key:value
    pairs.
    """
    pass

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
        # This little helper parses the header lines with
        # tags and values into a dict of dicts.
        
        # This dict contains the header line section names
        # and the number of splits of the data within the < >
        # parts
        headerSectionChoices={"INFO":3,"FORMAT":3,"FILTER":1}
        headerstuff=vcfHeader()
        for section in headerSectionChoices.keys():
            resub="##%s=<" % section
            # Grab the appropriate lines for each section
            lines=[re.sub(resub,"",line) for line in header \
                   if line.startswith("##%s" % section)]
            lines=[re.sub(">$","",line) for line in lines]
            headerInfo=[]
            # make a dict of the header information for each section.
            for line in lines:
                tagdict=dict([member.split("=",1) \
                              for member in line.split(",",headerSectionChoices[section])])
                headerInfo.append(tagdict)
            headerstuff[section]=dict([(x['ID'],x) for x in headerInfo])
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

