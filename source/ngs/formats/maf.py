import csv
import gzip
import sys
from ngs.genomicintervals import GenomicInterval

class MAFRecord(dict):
    def chrom(self):
        return row['Chromosome']
    def start(self):
        return row['Start_position']
    def end(self):
        return row['End_position']

class MAFFile(object):
    def __init__(self,fname):
        if(isinstance(fname,file)):
            self.fh=fname
        else:
            if(fname.endswith('.gz')):
                self.fh=gzip.GzipFile(fname)
            else:
                self.fh=open(fname,'r')
        self.reader=csv.DictReader(self.fh,delimiter="\t")
    def __iter__(self):
        for row in self.reader:
            if(not(row['Chromosome'].startswith('chr'))):
                row['Chromosome']='chr'+row['Chromosome']
            row['Start_position']=int(row['Start_position'])
            row['End_position']=int(row['End_position'])
            yield MAFRecord(row)
        
