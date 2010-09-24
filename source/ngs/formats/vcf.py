"""
A module for opening and parsing a VCF format file and encapsulating VCF records

The Variant Call Format (VCF) is described `here <http://1000genomes.org/wiki/doku.php?id=1000_genomes:analysis:vcf4.0>`_
"""

__docformat__ = 'restructuredtext'

import gzip
import re
import itertools

VCF_KEYS = "CHROM  POS     ID        REF   ALT    QUAL  FILTER  INFO".split()
VCF_KEYS_FORMAT = "CHROM  POS     ID        REF   ALT    QUAL  FILTER".split()

TRANSITIONS = dict()
for p in ["AG", "CT"]:
    for x in [p, ''.join(reversed(p))]:
        TRANSITIONS[x.lower()] = True
        TRANSITIONS[x] = True

def is_nan(x):
    return type(x) is float and x != x

def convertToType(chr, pos, d, onlyKeys = None):
    out = dict()
    types = [int, float, str]
    for key, value in d.items():
        if onlyKeys == None or key in onlyKeys:
            for type in types:
                try:
                    out[key] = type(value)
                    if is_nan(out[key]): 
                        #print 'Warning, nan found at %s:%s, using NaN string' % (chr, pos)
                        out[key] = 'NaN'
                    break
                except:
                    pass
        else:
            out[key] = value
    return out

class vcfHeader(dict):
    """
    Contains the header tag lines from a VCF file

    Currently, this class simply stores three dicts, INFO, FORMAT, and FILTER.
    Each of these dicts contains a dict of tags and potentially many key:value
    pairs.
    """
    pass

class vcfFile:
    """
    The entry point for parsing a VCF format file

    Initialize with a filename.  It the filename ends with ".gz",
    the file will be opened with gzip for reading.
    """
    def __init__(self,fname):
        self.fname=fname
        self.open()

    def parse(self):
        """Return a generator that yields one :class:`VCFRecord` at a time"""
        for line in self.fh:
            (yield string2VCF(line.strip(),self.header))

    def close(self):
        self.is_open=False
        self.fh.close()

    def open(self):
        if(self.fname.endswith('.gz')):
            self.fh=gzip.open(self.fname,'r')
        else:
            self.fh=open(self.fname,'r')
        self.is_open=True
        self.header=[]
        line=self.fh.readline()
        while(not (line.startswith("#CHROM"))):
            self.header.append(line.strip())
            line=self.fh.readline()
        self.header.append(line.strip())
        tableHeaders=self.header[-1]
        self.sampleNames=tableHeaders.split("\t")[9:]
        self.header=self._parseHeader(self.header)

    def _parseHeader(self,header):
        # This little helper parses the header lines with
        # tags and values into a dict of dicts.
        
        # This dict contains the header line section names
        # and the number of splits of the data within the < >
        # parts
        headerSectionChoices={"INFO":3,"FORMAT":3,"FILTER":1}
        headerstuff=vcfHeader()
        for section in headerSectionChoices.keys():
            resub="##%s=<" % section
            # Grab the appropriate lines for each section
            lines=[re.sub(resub,"",line) for line in header \
                   if line.startswith("##%s" % section)]
            lines=[re.sub(">$","",line) for line in lines]
            headerInfo=[]
            # make a dict of the header information for each section.
            for line in lines:
                tagdict=dict([member.split("=",1) \
                              for member in line.split(",",headerSectionChoices[section])])
                headerInfo.append(tagdict)
            headerstuff[section]=dict([(x['ID'],x) for x in headerInfo])
        return(headerstuff)

class VCFRecord:
    """Simple support for accessing a VCF record"""
    def __init__(self, basicBindings, header=None, rest=[], moreFields = dict(), decodeAll = True):
        self.header = header
        self.info = parseInfo(basicBindings["INFO"])
        chr, pos = basicBindings['CHROM'], basicBindings['POS']
        self.bindings = convertToType(chr, pos, basicBindings, onlyKeys = ['POS', 'QUAL'])
        self.bindings.update(moreFields)
        if decodeAll: self.info = convertToType(chr, pos, self.info)
        self.rest = rest
        self.samples=[dict(zip(rest[0].split(":"),y.split(":"))) for y in rest]

    
    def hasHeader(self): return self.header <> None
    def getHeader(self): return self.header
    
    def get(self, key): return self.bindings[key]
    
    def getChrom(self): return self.get("CHROM")
    def getPos(self): return self.get("POS")
    def getLoc(self): return str(self.getChrom()) + ':' + str(self.getPos())

    def getID(self): return self.get("ID")
    def isNovel(self): return self.getID() == "."
    def isKnown(self): return not self.isNovel()
    
    def getRef(self): return self.get("REF")
    def getAlt(self): return self.get("ALT")
    def isVariant(self): 
        v = self.getAlt() <> '.'
        #print 'isVariant', self.bindings, v
        return v

    def getQual(self): return self.get("QUAL")
    
    def getVariation(self): return self.getRef() + self.getAlt()

    def isTransition(self): 
        #print self.getVariation(), TRANSITIONS
        return self.getVariation() in TRANSITIONS 
    def isTransversion(self): 
        return not self.isTransition() 
    
    def getFilter(self): return self.get("FILTER")
    def failsFilters(self): return not self.passesFilters()
    def passesFilters(self):
        v = self.getFilter() == "." or self.getFilter() == "0" or self.getFilter() == 'PASS'
        #print self.getFilter(), ">>>", v, self
        return v
        

    def hasField(self, field):
        return field in self.bindings or field in self.info 

    def setField(self, field, value):
        assert value <> None
        
        #print 'setting field', field, value
        #print 'getInfo', self.getInfo()
        if field in self.bindings:
            self.bindings[field] = value
        else: 
            self.info[field] = value
            #self.setField("INFO", self.getInfo())
        #print 'getInfo', self.getInfo()
    
    def getField(self, field, default = None):
        if field in self.bindings:
            return self.get(field)
        elif field in self.getInfoDict():
            return self.getInfoKey(field)
        else:
            return default
    
    #def getInfo(self): return self.get("INFO")
    def getInfo(self): 
        def info2str(x,y):
            if type(y) == bool or x == '.':
                return str(x)
            else:
                return str(x) + '=' + str(y)
        v = ';'.join(map(lambda x: info2str(*x), sorted(self.info.iteritems(), key=lambda x: x[0])))
        if v == "":
            v = "."
        #print 'V = ', v
        return v

    def getInfoDict(self): return self.info
    
    def getInfoKey(self, name, default = None): 
        info = self.getInfoDict()
        if name in info:
            return info[name]
        else:
            return default
            
    def infoHasKeys(self, keys):
        return all(map(lambda key: key in self.getInfo(), keys))
       
    def __str__(self):
        #return str(self.bindings) + " INFO: " + str(self.info) 
        return ' '.join(['%s=%s' % (x,y) for x,y in self.bindings.iteritems()])
        
    def format(self):
        return '\t'.join([str(self.getField(key)) for key in VCF_KEYS_FORMAT] + [self.getInfo()] + self.rest)

def parseInfo(s):
    d = dict()
    if s != "":
        for elt in s.split(";"):
            if '=' in elt:
                key, val = elt.split('=')
            else:
                key, val = elt, 1
            d[key] = val
    return d


def string2VCF(line, header=None, decodeAll = True):
    if line[0] != "#":
        s = line.split()
        bindings = dict(zip(VCF_KEYS, s[0:8]))
        moreFields = dict()
        #print 'HELLO', header, s, decodeAll
        #if header <> None and decodeAll: 
            #moreFields = dict(zip(header[8:], s[8:]))
            #print header, moreFields
        return VCFRecord(bindings, header, rest=s[8:], moreFields = moreFields, decodeAll = decodeAll)
    else:
        return None

    # we reach this point for empty files    
    #print 'header is', header
    return header, columnNames, []

def formatVCF(header, records):
    #print records
    #print records[0]
    return itertools.chain(header, itertools.imap(VCFRecord.format, records)) 
 

