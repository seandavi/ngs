#!/usr/bin/env python
# encoding: utf-8
"""
regions.pyx

Created by Sean Davis on 2010-08-16.
Copyright (c) 2010 __US Government__. All rights reserved.
"""

import sys
import os
import unittest
from operator import itemgetter
import pysam

from bx.intervals.intersection import IntervalTree

class Range:
    """Encapsulates a range on a line, as in a range on a chromosome.

    Note that these are 0-based, half-open ranges."""
    def __init__(self,rbeg,rend):
        self.rbeg=rbeg
        self.rend=rend
        
class Region(Range):
    """Inherited from Range, a Region represents a genomic region and
    includes the chromosome."""
    def __init__(self,chromosome,rbeg,rend):
        Range.__init__(self,rbeg,rend)
        self.chromosome=chromosome

    def __str__(self):
        return("<ngs.regions.Region [%s:%d-%d]>" % (self.chromosome,self.rbeg,self.rend))
        
class RegionList(dict):
    """A RegionList is a list of Regions on the chromosome.  This implementation
    is backed by a bx-python IntervalTree and is pretty fast, performing about
    3M overlap queries per minute with a list of 100k regions in the list"""
    
    def add(self,region):
        """Add a new Region-like object to the RegionList"""
        try:
            self[region.chromosome].insert(region.rbeg,region.rend,region)
        except KeyError:
            itree = IntervalTree()
            itree.insert(region.rbeg,region.rend,region)
            self[region.chromosome]=itree

    def addObject(self,chromosome,rbeg,rend,obj,strand="+"):
        try:
            self[chromosome].insert(rbeg,rend,obj)
        except KeyError:
            itree = IntervalTree()
            itree.insert(rbeg,rend,obj)
            self[chromosome]=itree
    
    def overlapCount(self,region):
        """Find the number of regions that overlap the given Region-like object"""
        return(len(self.getOverlaps(regions)))

    def getOverlaps(self,region):
        """Find actual regions that overlap the given Region-like object"""
        try:
            return(self[region.chromosome].find(region.rbeg,region.rend))
        except KeyError:
            return([])


class Transcript(Region):
    def __init__(self,chromosome,name,exons,cds,strand):
        exons.sort()
        Region.__init__(self,chromosome,exons[0][0],exons[-1][1])
        self.name=name
        self.strand=strand
        self.exons=exons
        self.cds=cds
        self.introns=self._computeIntrons()
        

    def __str__(self):
        return("Transcript <%s:%s %s:%s>" %
               (self.name,self.strand,self.chromosome,str(self.exons)))

    def _computeIntrons(self):
        self.exons.sort()
        intronstarts=[x[1] for x in self.exons[0:-1]]
        intronends  =[x[0] for x in self.exons[1:]]
        introns=zip(intronstarts,intronends)
        return(introns)

    def overlaps(self,pos):
        types=[]
        for exon in self.exons:
            if((pos>exon[0]) & (pos<=exon[1])):
                if((pos>self.cds[0]) & (pos<=self.cds[1])):
                    types.append('coding')
                else:
                    if(pos>self.cds[1]):
                        if(self.strand=='+'):
                            types.append("3'-UTR")
                        else:
                            types.append("5'-UTR")
                    if(pos<=self.cds[0]):
                        if(self.strand=='+'):
                            types.append("5'-UTR")
                        else:
                            types.append("3'-UTR")
        maxp=max(self.exons,key=itemgetter(1))[1]
        minp=min(self.exons,key=itemgetter(0))[0]
        if((pos>minp) & (pos<=maxp)):
            for exon in self.exons:
                if(((pos>exon[0]-2) & (pos<=exon[0])) |
                   ((pos>exon[1]) & (pos<=exon[1]+2))):
                    types.append('splice-site')
        for intron in self.introns:
            if((pos>intron[0]) & (pos<=intron[1])):
                if((pos>self.cds[0]) & (pos<=self.cds[1])):
                    types.append('intron')
        return(types)

class TabixBackedRegionList(object):
    """This is a pickleable class meant to be used as a storage backend
    for genomic regions"""
    
    def __init__(self,fname,build='hg18'):
        self.build=build
        self.fname=fname
        self._file=pysam.Tabixfile(fname,'r')

    # __getstate__ is used to pass information to pickle
    # note that we exclude the file handle below.  
    def __getstate__(self):
        ret = self.__dict__.copy()
        del ret['_file']
        return ret

    # __setstate__ is used to get information in the
    # form of a dict from pickle.  We reconstitute
    # the file using the fname attribute.  Note
    # that the the update is not needed here,
    # but in some cases we would want to remove
    # things from the unpickled dict before proceeding.
    # In those cases, we would del() from "d" and then
    # update the self.__dict__.
    def __setstate__(self, d):
        self._file=pysam.Tabixfile(d['fname'])
        self.__dict__.update(d)

    def fetch(self,reference=None,start=None,end=None,region=None,parser=None):
        return(self._file.fetch(reference=None,start=None,end=None,region=None,parser=None))
