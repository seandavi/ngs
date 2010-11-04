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
    
    def overlapCount(self,region):
        """Find the number of regions that overlap the given Region-like object"""
        try:
            return(len(self[region.chromosome].find(region.rbeg,region.rend)))
        except KeyError:
            return(0)
