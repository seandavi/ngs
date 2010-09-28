
class ParseFastQ(object):
    """Returns a read-by-read fastQ parser analogous to file.readline()
    
    :param filePath: path or filename of fastq file
    :type filePath: string
    :param headerSymbols: list of length 2 specifying the header line start symbols; default ['@','+']
    :type headerSymbols: list of strings
    :rtype: tuple (seqHeader,seqStr,qualHeader,qualStr)

    Exmpl: parser.next()
    -OR-
    It's an iterator so you can do:
    for rec in parser:
    ... do something with rec ...


    .. todo::

        This should return fastq objects at some point
    """
    
    def __init__(self,filePath,headerSymbols=['@','+']):
        """Returns a read-by-read fastQ parser analogous to file.readline().

        :param filePath: path or filename of fastq file
        :param headerSymbols: list of length 2 specifying the header line start symbols; default ['@','+']::
        
            Exmpl: parser.next()
            -OR-
            It's an iterator so you can do:
            for rec in parser:
            ... do something with rec ...
    
        rec is a tuple: (seqHeader,seqStr,qualHeader,qualStr)
        """
        self._file = open(filePath, 'rU')
        self._currentLineNumber = 0
        self._hdSyms = headerSymbols
        
    def __iter__(self):
        return self
    
    def next(self):
        """Reads in next element, parses, and does minimal verification.
        :rtype: tuple: (seqHeader,seqStr,qualHeader,qualStr)"""
        # ++++ Get Next Four Lines ++++
        elemList = []
        for i in range(4):
            line = self._file.readline()
            self._currentLineNumber += 1 ## increment file position
            if line:
                elemList.append(line.strip('\n'))
            else: 
                elemList.append(None)
        
        # ++++ Check Lines For Expected Form ++++
        trues = [bool(x) for x in elemList].count(True)
        nones = elemList.count(None)
        # -- Check for acceptable end of file --
        if nones == 4:
            raise StopIteration
        # -- Make sure we got 4 full lines of data --
        assert trues == 4,\
               "** ERROR: It looks like I encountered a premature EOF or empty line.\n\
               Please check FastQ file near line #%s (plus or minus ~4 lines) and try again**" % (self._currentLineNumber)
        # -- Make sure we are in the correct "register" --
        assert elemList[0].startswith(self._hdSyms[0]),\
               "** ERROR: The 1st line in fastq element does not start with '%s'.\n\
               Please check FastQ file and try again **" % (self._hdSyms[0])
        assert elemList[2].startswith(self._hdSyms[1]),\
               "** ERROR: The 3rd line in fastq element does not start with '%s'.\n\
               Please check FastQ file and try again **" % (self._hdSyms[1])
        
        # ++++ Return fatsQ data as tuple ++++
        return tuple(elemList)
    
    def getNextReadSeq(self):
        """Convenience method: calls self.getNext and returns only the readSeq."""
        try:
            record = self.next()
            return record[1]
        except StopIteration:
            return None
