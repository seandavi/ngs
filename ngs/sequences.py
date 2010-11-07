import pyfasta

class GenomeDB(object):
    """Represents a genome's worth of fasta.  The idea is to have a single FASTA file with
    a genome of fasta in it.  Wrap this up in a little container with the build attached.

    Basic usage
    ^^^^^^^^^^^
    >>> import ngs.sequences
    >>> fa = ngs.sequences.GenomeDB('testdata/exampleFASTA.fasta',build='testing')
    >>> fa.seqLengths()
    {'chr1': 100000L}
    """
    
    def __init__(self,fastafile,build):
        self._fasta=pyfasta.Fasta(fastafile)
        self.build = build

    def getSequence(self,chromosome,start,end,strand='+'):
        """
        Retrieve sequence as simple string, zero-based, half-open coordinates
        :param chromosome: chromosome name
        :param start: end > start
        :param end: end > start
        :param strand: "+","-", default "+".  Result is reverse complemented if strand is "-"
        """
        return(self._fasta.sequence({'chr':chromosome,
                                     'start':start,
                                     'end':end,
                                     'strand':strand}))

    def keys(self):
        """
        Return chromosome names available
        """
        return(sorted(self._fasta.keys()))

    def seqLengths(self):
        """
        Return a dict of chromosome:length pairs
        """
        lens={}
        for k in self.keys():
            fa_tmp=self._fasta[k]
            lens[k]=fa_tmp.stop-fa_tmp.start
        return(lens)
                                     
