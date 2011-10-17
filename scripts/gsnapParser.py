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
    def __repr__(self):
        return("<GsnapRead with %d alignments>" % (len(self.alignments)))

class GsnapAlignment(object):
    def __init__(self,line):
        self.info = line
        self.blocks = [line]
    def __repr__(self):
        return("<GsnapAlignment with %d blocks>" % (len(self.blocks)))

class GsnapBlock(object):
    def __init__(self,line):
        self.info = line

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
        print rec

    print j
