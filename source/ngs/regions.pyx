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
        
class RegionList(dict):
    
    def add(self,region):
        """Add a new Region-like object to the RegionList"""
        try:
            self[region.chromosome].add(region)
        except KeyError:
            binlist = BinList()
            binlist.add(region)
            self[region.chromosome]=binlist
    
    def overlapCount(self,region):
        """Find the number of regions that overlap the given Region-like object"""
        try:
            return(self[region.chromosome].overlapCount(region))
        except KeyError:
            return(0)

class BinList(dict):
    """Designed to hold ranges and supports very fast range queries on a single
    linear range like a chromosome."""
    def add(self,range):
        """Add a new range-like object to the BinList"""
        newbin=self._reg2bin(range.rbeg,range.rend)
        if(self.has_key(newbin)):
            self[newbin].append(range)
        else:
            l = [range]
            self[newbin]=l
            
    def overlapCount(self,range):
        bins = self._reg2bins(range.rbeg,range.rend)
        retcount = 0
        for bin in bins:
            try:
                candidates = self[bin]
                for candidate in candidates:
                    if(((candidate.rbeg<=range.rbeg) & (candidate.rend>=range.rbeg)) |
                        ((candidate.rbeg<=range.rend) & (candidate.rbeg>=range.rend)) |
                        ((candidate.rbeg<=range.rbeg) & (candidate.rend>=range.rend)) |
                        ((candidate.rbeg>=range.rbeg) & (candidate.rend<=range.rend))):
                        retcount+=1
            except KeyError:
                pass
        return(retcount)
        
    def _reg2bin(self, rbeg, rend):
        rend=rend-1
        if (rbeg>>14 == rend>>14): return ((1<<15)-1)/7 + (rbeg>>14)
        if (rbeg>>17 == rend>>17): return ((1<<12)-1)/7 + (rbeg>>17)
        if (rbeg>>20 == rend>>20): return ((1<<9)-1)/7 + (rbeg>>20)
        if (rbeg>>23 == rend>>23): return ((1<<6)-1)/7 + (rbeg>>23)
        if (rbeg>>26 == rend>>26): return ((1<<3)-1)/7 + (rbeg>>26)
        return(0)
    
    def _reg2bins(self, rbeg, rend):
        i=0
        rend=rend-1
        retlist=list()
        retlist.append(0)
        for k in range(1 + (rbeg>>26), 1 + (rend>>26)+1): retlist.append(k)
        for k in range(9 + (rbeg>>23), 9 + (rend>>23)+1): retlist.append(k)
        for k in range(73 + (rbeg>>20), 73 + (rend>>20)+1): retlist.append(k)
        for k in range(585 + (rbeg>>17), 585 + (rend>>17)+1): retlist.append(k)
        for k in range(4681 + (rbeg>>14), 4681 + (rend>>14)+1): retlist.append(k)
        return(retlist)


class BinListTests(unittest.TestCase):
    def setUp(self):
        self.binlist = BinList()
        
    def test_reg2bin(self):
        self.assertEqual(self.binlist._reg2bin(100,2000),4681)
        
    def test_reg2bins(self):
        self.assertEqual(self.binlist._reg2bins(100,2000),[0, 1, 9, 73, 585, 4681])
        
    def test_add(self):
        self.binlist.add(Range(100,2000))
        self.assertEqual(len(self.binlist[4681]),1)

    def test_overlapCount(self):
        self.binlist.add(Range(100,2000))
        self.assertEqual(self.binlist.overlapCount(Range(150,300)),1)
        
    def test_overlapCountNoOverlap(self):
        self.binlist.add(Range(100,200))
        self.assertEqual(self.binlist.overlapCount(Range(400,500)),0)
        
    def test_regionOverLapCount(self):
        regionlist = RegionList()
        a = Region("chr1",100,200)
        regionlist.add(a)
        self.assertEqual(regionlist.overlapCount(Region("chr1",105,195)),1)
        

if __name__ == '__main__':
        unittest.main()
