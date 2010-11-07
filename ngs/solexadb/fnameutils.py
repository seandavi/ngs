import re

BNAME_WITH_READNO_RE = re.compile("(?P<lane>[1-8])_(?P<read>[12,]*)_(?P<flowcell>\w+)\.(?P<id>[^\.]+)(?P<extension>.*)")
BNAME_WITHOUT_READNO_RE = re.compile("(?P<lane>[1-8])_(?P<flowcell>\w+)\.(?P<id>[^\.]+)(?P<extension>.*)")

def parseFname(fname,withReadNumber=False):
    """
    Parse a standard sequence/export/summary filename into parts

    :param fname: String filename from from the solexa database
    :param withReadNumber: Boolean indicating whether or not the read number is included in the filename
    :rtype: dict with several keys including lane, flowcell, id, extension ('' if none), and when withReadNumber=True, read

    >>> import ngs.solexadb.fnameutils as fnutils
    >>> fnutils.parseFname("1_1,2_622RWAAXX.154_BUSTARD-2010-08-31.tgz",withReadNumber=True)
    {'read': '1,2', 'lane': '1', 'flowcell': '622RWAAXX', 'id': '154_BUSTARD-2010-08-31', 'extension': '.tgz'}
    >>> fnutils.parseFname("1_1_622RWAAXX.154_BUSTARD-2010-08-31.tgz",withReadNumber=True)
    {'read': '1', 'lane': '1', 'flowcell': '622RWAAXX', 'id': '154_BUSTARD-2010-08-31', 'extension': '.tgz'}
    >>> fnutils.parseFname("1_622RWAAXX.154_BUSTARD-2010-08-31.bam")
    {'lane': '1', 'flowcell': '622RWAAXX', 'id': '154_BUSTARD-2010-08-31', 'extension': '.bam'}
    """
    if(withReadNumber):
        return(BNAME_WITH_READNO_RE.match(fname).groupdict())
    return(BNAME_WITHOUT_READNO_RE.match(fname).groupdict())

def getBasename(fname,withReadNumber=False,retWithReadNumber=False):
    """
    Parse a standard sequence/export/summary filename into parts

    :param fname: String filename from from the solexa database
    :param withReadNumber: Boolean indicating whether or not the read number is included in the filename
    :param retWithReadNumber: Boolean indicating whether or not to return the read number with the basename
    :rtype: dict with several keys including lane, flowcell, id, extension ('' if none), and when withReadNumber=True, read

    >>> import ngs.solexadb.fnameutils as fnutils
    >>> fnutils.getBasename("1_1,2_622RWAAXX.154_BUSTARD-2010-08-31.tgz",withReadNumber=True,retWithReadNumber=True)
    '1_1,2_622RWAAXX.154_BUSTARD-2010-08-31'
    >>> fnutils.getBasename("1_1_622RWAAXX.154_BUSTARD-2010-08-31.tgz",withReadNumber=True,retWithReadNumber=True)
    '1_1_622RWAAXX.154_BUSTARD-2010-08-31'
    >>> fnutils.getBasename("1_622RWAAXX.154_BUSTARD-2010-08-31.bam")
    '1_622RWAAXX.154_BUSTARD-2010-08-31'
    """    

    retdict = parseFname(fname,withReadNumber)
    if(retWithReadNumber):
        return("%(lane)s_%(read)s_%(flowcell)s.%(id)s" % (retdict))
    else:
        return("%(lane)s_%(flowcell)s.%(id)s" % (retdict))
    
        

    
    
