#!/usr/bin/env python
import csv
import sys

f = open(sys.argv[1],'r')
reader = csv.reader(f,delimiter="\t")
reader.next()
for row in reader:
    acc=row[1]
    chrom=row[2].replace('chr','')
    name=row[12]
    if(row[3]=="+"):
        starts=[int(x) for x in row[9].split(",")[:-1]]
        ends=[int(x) for x in row[10].split(",")[:-1]]
        print ">%s.%s.exon%d %s:%d..%d donor" % (acc,name,1,chrom,ends[0],ends[0]+1)
        for y in range(len(starts)-2):
            print ">%s.%s.exon%d %s:%d..%d acceptor" % (acc,name,y+1,chrom,starts[y+1],starts[y+1]+1)
            print ">%s.%s.exon%d %s:%d..%d donor" % (acc,name,y+1,chrom,ends[y+1],ends[y+1]+1)
        print ">%s.%s.exon%d %s:%d..%d acceptor" % (acc,name,len(starts),chrom,starts[len(starts)-1]+1,starts[len(starts)-1]+1)
    elif(row[3]=="-"):
        starts=[int(x) for x in row[10].split(",")[:-1]]
        ends=[int(x) for x in row[9].split(",")[:-1]]
        ends.reverse()
        starts.reverse()
        print ">%s.%s.exon%d %s:%d..%d donor" % (acc,name,1,chrom,ends[0]+1,ends[0])
        for y in range(len(starts)-2):
            print ">%s.%s.exon%d %s:%d..%d acceptor" % (acc,name,y+1,chrom,starts[y+1]+1,starts[y+1])
            print ">%s.%s.exon%d %s:%d..%d donor" % (acc,name,y+1,chrom,ends[y+1]+1,ends[y+1])
        print ">%s.%s.exon%d %s:%d..%d acceptor" % (acc,name,len(starts),chrom,starts[len(starts)-1]+1,starts[len(starts)-1])
        
