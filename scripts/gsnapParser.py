#!/usr/bin/env python
import gzip
import collections

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
        self.readinfo = line
        self.alignments = []

class GsnapAlignment(list):
    def __init__(self,line):
        self.aligninfo = line
        self.blocks = []

class GsnapFile(object):
    def __init__(self,f):
        self.fh = openFile(f)
        self.nextline= self.fh.next()
        self.nextRecord = self._getNextRecord()

    def _getReads(self,lines):
        curread = None
        curalign= None
        recs = []
        for i in range(len(lines)):
            if(lines[i].startswith('>') or lines[i].startswith('<')):
                if(curread is not None):
                    recs.append(curread)
                curread = {'alignments':[],'read':lines[i]}
            if(lines[i].startswith(' ')):
                if(curalign is not None):
                    curread['alignments'].append(curalign)
                curalign = {'blocks':[],'alignment':lines[i]}
            if(lines[i].startswith(',')):
                curalign['blocks'].append(lines[i])
        return(recs)
               

    def _getNextRecord(self):
        line = self.nextline
        lines=[]
        lines.append(line)
        line = self.fh.next()
        while(not (line.startswith('>'))):
            lines.append(line)
            line = self.fh.next()
        self.nextline=line
        curread = None
        curalign= None
        recs = []
        for i in range(len(lines)):
            if(lines[i].startswith('>') or lines[i].startswith('<')):
                if(curread is not None):
                    recs.append(curread)
                curread = {'alignments':[],'read':lines[i]}
            if(lines[i].startswith(' ')):
                if(curalign is not None):
                    curread['alignments'].append(curalign)
                curalign = {'blocks':[],'alignment':lines[i]}
            if(lines[i].startswith(',')):
                curalign['blocks'].append(lines[i])
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
    for rec in g:
        print rec
        
