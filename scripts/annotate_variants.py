#!/usr/bin/env python
import tempfile
import urllib2
import gzip
import os
import sys
import optparse
import gzip
import csv

import ngs.regions

def gunzip(fname):
    f = gzip.GzipFile(fname,'rb')
    oname = fname.replace(".gz","")
    o = open(oname,'w')
    o.write(f.read())
    o.close()
    f.close()
    return(oname)

class UCSC:
    urlstring = "http://hgdownload.cse.ucsc.edu/goldenPath/%s/database/"
    
    def __init__(self,build):
        self.build=build

    def _get_url(self):
        return(self.urlstring % (self.build))

    url=property(_get_url,None,None,"The url for download")

    def get_table(self,tablebase,destdir=tempfile.gettempdir(),unzip=True):
        flocalfname = os.path.join(destdir,tablebase + ".txt.gz")
        if(os.path.exists(flocalfname)):
            return(flocalfname)
        f = urllib2.urlopen(self.url + tablebase + ".txt.gz")
        flocal = open(flocalfname,'wb')
        flocal.write(f.read())
        flocal.close()
        return(flocalfname)

def do_gene_based_annotation(opts,args):
    with open("/Users/sdavis/Downloads/CCDS.hg18 (1).bed",'r') as bedfile:
        bedfile.next() #skip header
        n=0
        reglist = ngs.regions.RegionList()
        for line in bedfile:
            sline = line.strip().split("\t")
            exonstarts=map(int,sline[9].split(",")[0:-1])
            exonends=map(int,sline[10].split(",")[0:-1])
            cds = (int(sline[6]),int(sline[7]))
            exons = zip(exonstarts,exonends)
            t = ngs.regions.Transcript(chromosome=sline[2],
                                       name=sline[1],exons=exons,
                                       strand=sline[3],cds=cds)
            reglist.add(t)
        
    with open(args[0]) as varfile:
        for row in csv.reader(varfile,delimiter="\t"):
            r = ngs.regions.Region(row[0],int(row[1])-1,int(row[1]))
            transcripts = reglist.getOverlaps(r)
            if(len(transcripts)>0):
                print ":".join([x.name for x in transcripts])
                for transcript in transcripts:
                    print row,transcript.overlaps(r.rend)



if __name__=="__main__":
    parser = optparse.OptionParser()
    parser.add_option("-b","--genome-build",dest="genome",
                      help="UCSC genome build (hg18, mm9, etc.)")
    parser.add_option("--splice-pad",dest="splice_pad",default=2,
                      type="int",help="Number of bases to add to exon to be considered a splice site")
    parser.add_option("--table-name",dest="table_name",
                      help="The UCSC table name that will be used to grab data")
    parser.add_option("-d","--datadir",dest="datadir",default='.',
                      help="The data directory root to which data will be downloaded")
    parser.add_option("--start-column",dest="start_column",default=3,
                      type="int",help="The table column that represents the start location on the genome (first column is 1)")
    parser.add_option("--end-column",dest="end_column",default=4,
                      type="int",help="The table column that represents the end location on the genome (first column is 1)")
    parser.add_option("--chrom-column",dest="chrom_column",default=2,
                      type="int",help="The table column that represents the chrom location on the genome (first column is 1)")
    parser.add_option("-g","--gene-based-annotation",
                      dest="gene_based",action="store_true",
                      default=False,help="Do gene-based annotation")
    
    (opts,args)=parser.parse_args()
    if(opts.gene_based):
        do_gene_based_annotation(opts,args)
    ucsc = UCSC(opts.genome)
    print (dir(ngs.regions.RegionList))
    fname=ucsc.get_table(tablebase=opts.table_name,destdir=opts.datadir)
    n=1
    reglist = ngs.regions.RegionList()
    for line in open(args[0]):
        sline = line.strip().split()
        r=ngs.regions.Region(sline[0],
                             int(sline[1])-1,
                             int(sline[1]))
        reglist.add(r)
    j = 0
    for line in gzip.GzipFile(fname):
        j+=1
        if((j % 10000) == 0): print j
        sline = line.strip().split("\t")
        r=ngs.regions.Region(sline[1],
                             int(sline[2]),
                             int(sline[3]))
        for x in reglist.getOverlaps(r):
            print("%s\t%s" % (x,r))
