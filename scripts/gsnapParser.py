#!/usr/bin/env python
import gzip
import collections
import re

POSITION_REGEX = re.compile('([+-])(.*):(\d+)..(\d+)')
FIRSTTAG_REGEX = re.compile('(.*):(\d+)..(.*):(\d+)')


def openFile(f):
    if(isinstance(f,file)):
        return(f)
    if(isinstance(f,gzip.GzipFile)):
        return(f)
    if(f.endswith('.gz')):
        return(gzip.GzipFile(f))
    else:
        return(open(f))

class GsnapRecord(list):
    pass

#GsnapRead = collections.namedtyple('GsnapRead','read type qual readname alignments')



class GsnapRead(object):
    def __init__(self,line):
        sline = line.strip().split("\t")
        self.read = sline[0][1:]
        tmp = sline[1].split(" ")
        self.naligns = int(tmp[0])
        self.readtype= tmp[1]
        self.is_translocation=False
        if(len(tmp)>2):
            self.is_translocation=True
        self.readname = sline[3]
        self.quality  = sline[2]
        self.alignments = []
    def __repr__(self):
        return("<GsnapRead with %d alignments, %s>" % (self.naligns,self.readname))

class GsnapAlignment(object):
    def __init__(self,line):
        self.blocks = [GsnapBlock(line)]
    def __repr__(self):
        return("<GsnapAlignment with %d blocks>" % (len(self.blocks)))

class GsnapBlock(object):
    def __init__(self,line):
        sline = line.strip().split("\t")
        self.alignstring = sline[0][1:]
        (self.blockstart,self.blockend) = map(int,sline[1].split(".."))
        m = POSITION_REGEX.match(sline[2])
        self.chrom = m.group(2)
        self.strand = m.group(1)
        if(self.strand=='+'):
            self.start  = int(m.group(3))
            self.end    = int(m.group(4))
        else:
            self.end    = int(m.group(4))
            self.start  = int(m.group(3))
        tmpdat = sline[3].split(",")
        m = FIRSTTAG_REGEX.match(tmpdat[0])
        self.is_start=False
        self.is_end  =False
        self.startclip=0
        self.endclip  =0
        if(m.group(1)=='start'):
            self.is_start=True
            self.startclip = int(m.group(2))
        if(m.group(3)=='end'):
            self.is_end  =True
            self.endclip = int(m.group(4))
        self.tmpmap = dict([x.split(":") for x in tmpdat[1:]])
        

class GsnapFile(object):
    def __init__(self,f):
        self.fh = openFile(f)
        self.nextline= self.fh.next()
        self.nextRecord = self._getNextRecord()

    def _getNextRecord(self):
        if(self.nextline==''):
            return(None)
        line = self.nextline
        lines=[]
        lines.append(line)
        line = self.fh.next()
        while(not (line.startswith('>')) & (line!='')):
            lines.append(line)
            line = self.fh.next()
        self.nextline=line
        curread = None
        curalign= None
        recs = []
        for i in range(len(lines)):
            if(lines[i].startswith('>') or lines[i].startswith('<')):
                if(curread is not None):
                    if(curalign is not None):
                        curread.alignments.append(curalign)
                    recs.append(curread)
                curread = GsnapRead(lines[i])
            if(lines[i].startswith(' ')):
                if(curalign is not None):
                    curread.alignments.append(curalign)
                curalign = GsnapAlignment(lines[i])
            if(lines[i].startswith(',')):
                curalign.blocks.append(GsnapBlock(lines[i]))
        recs.append(curread)
        return(recs)

    def __iter__(self):
        return(self)

    def next(self):
        if(self.nextRecord is not None):
            rec = self.nextRecord
            self.nextRecord = self._getNextRecord()
            return(rec)
        else:
            raise StopIteration




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    opts = parser.parse_args()
    g = GsnapFile(opts.filename)
    j = 0
    for rec in g:
        j+=1
        for read in rec:
            for align in read.alignments:
                for block in align.blocks:
                    print read.readname,block.blockstart,block.start,block.end,block.is_start,block.is_end,block.tmpmap

    print j
