class Transcript(object):
    def __init__(self,name,chromosome,txStart,txEnd,cdsStart,cdsEnd,
                 strand,exonStarts,exonEnds):
        self.name=name
        self.chromosome=chromosome
        (self.txStart,self.txEnd)=sorted([txStart,txEnd])
        (self.cdsStart,self.cdsEnd)=sorted([cdsStart,cdsEnd])
        self.strand=strand
        if(len(exonStarts)<>len(exonEnds)):
            raise Exception("exonStarts and exonEnds are not the same size")
        self.exons=zip(sorted(exonStarts),sorted(exonEnds))

class TranscriptDB(object):
    def __init__(self,genome='hg18'):
        self.genome=genome
        self.transcripts=[]

    def add(self,name,txStart,txEnd,cdsStart,cdsEnd,strand,exonStarts,exonEnds):
        self.transcripts.append(Transcript(name,txStart,txEnd,
                                           cdsStart,cdsEnd,strand,
                                           exonStarts,exonEnds))
    def addTranscript(self,transcript):
        self.transcripts.append(trancript)
