from bx.intervals import IntervalTree
from bx.intervals import Interval

class GenomicInterval(Interval):
    def __init__(self,chrom,start,end,value=None,strand=None):
        Interval.__init__(self,start,end,value)
        self.chrom=chrom
        self.strand=strand

class GenomicIntervalTree(dict):
    def add_interval(self,genintrval):
        if(genintrval.chrom in self):
            self[genintrval.chrom].add_interval(genintrval)
        else:
            self[genintrval.chrom]=IntervalTree()
            self[genintrval.chrom].add_interval(genintrval)
    def find(self,chrom,start,end):
        if(chrom not in self):
            return([])
        return(self[chrom].find(start,end))
