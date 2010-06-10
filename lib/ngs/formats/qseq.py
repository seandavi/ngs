#!/usr/bin/env python
# encoding: utf-8
"""
qseq.py

Created by Sean Davis on 2010-06-08.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import unittest

class qseqRecord:
	def __init__(self,line):
		fields=line.strip().split("\t")
		self.machine=fields[0]
		self.run=fields[1]
		self.lane=int(fields[2])
		self.tile=int(fields[3])
		self.xcoord=int(fields[4])
		self.ycoord=int(fields[5])
		self.indexnum=int(fields[6])
		self.read=int(fields[7])
		self.sequence=fields[8]
		self.quality=fields[9]
		self.filter=bool(fields[10])

class qseq:
	def __init__(self,fname):
		if(fname.endswith("gz")):
			self.fh=gzip.open(fname,"r")
		else:
			self.fh=open(fname,'r')
	
	def 
	
		
			
			


class qseqTests(unittest.TestCase):
	def setUp(self):
		pass


if __name__ == '__main__':
	unittest.main()