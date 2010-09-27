import ngs.regions
import gzip
import shlex

class GTFRecord(ngs.regions.Region):
    """
    Represents a GTF line

    GTF stands for Gene transfer format. It borrows from GFF, but has additional structure that warrants a separate definition and format name.
    Structure is as GFF, so the fields are:
    <chromosome> <source> <feature> <rbeg> <rend> <score> <strand> <frame> [attributes] [comments]

    Here is a simple example with 3 translated exons. Order of rows is not important.::

        381 Twinscan  CDS          380   401   .   +   0  gene_id "001"; transcript_id "001.1";
        381 Twinscan  CDS          501   650   .   +   2  gene_id "001"; transcript_id "001.1";
        381 Twinscan  CDS          700   707   .   +   2  gene_id "001"; transcript_id "001.1";
        381 Twinscan  start_codon  380   382   .   +   0  gene_id "001"; transcript_id "001.1";
        381 Twinscan  stop_codon   708   710   .   +   0  gene_id "001"; transcript_id "001.1";

    The whitespace in this example is provided only for readability. In GTF, fields must be separated by a single TAB and no white space.
    """

    def __init__(self,line):
        parts = line.strip().split("\t")
        ngs.regions.Region.__init__(self,parts[0],
                                    int(parts[3]),
                                    int(parts[4]))
        self.source=parts[1]
        self.feature=parts[2]
        self.score=parts[5]
        self.strand=parts[6]
        self.frame=parts[7]
        # frame can be 0, 1, or 2 or a "." for not applicable
        try:
            self.frame=int(self.frame)
        except:
            pass
        self.rest=parts[8]
        self._parseAnnotationCol(parts[8])
        
    def _parseAnnotationCol(self,coltext):
        """
        Parse the last GTF column to pull out gene and transcript IDs
        """
        for possiblePair in coltext.split(";"):
            splitVals = shlex.split(possiblePair)
            if(len(splitVals)<>2):
                continue
            if(splitVals[0]=="gene_id"):
                self.gene=splitVals[1]
            if(splitVals[0]=="transcript_id"):
                self.transcript=splitVals[1]
            
        
    def __str__(self):
        return("%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\t%s\t" % (
            self.chromosome,
            self.source,
            self.feature,
            self.rbeg,
            self.rend,
            str(self.score),
            self.strand,
            str(self.frame),
            self.rest))

class GTFReader:
    """
    Read a GTF file
    """

    def __init__(self,fname=None,fh=None):
        if(fname is not None):
            self.fh=self._open(fname)
        elif(fh is not None):
            self.fh=fh
        else:
            raise(Exception("Must specify either fname or fh"))
        
    def _open(self,fname):
        fh=None
        if(fname.endswith('.gz')):
            fh=gzip.open(fname,'r')
        else:
            fh=open(fname,'r')
        return(fh)

    def parse(self):
        """Return a generator that yields one :class:`VCFRecord` at a time"""
        for line in self.fh:
            (yield GTFRecord(line))
            
