#!/usr/bin/env python
import optparse
import csv
import sys

def somatic2annovar(fname):
    csvfile = csv.reader(open(fname,'r'),delimiter="\t")
    csvfile.next()
    for row in csvfile:
        if(row[9]==""): 
            row[9]="-"
            row[7]=str(int(row[7])+1)
        if(row[10]==""): row[10]="-"
        print "\t".join([row[5],row[6],
                        row[7],row[9],
                        row[10],row[13],row[14]])

if __name__=="__main__":
    somatic2annovar(sys.argv[1])
