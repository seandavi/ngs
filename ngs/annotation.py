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

    def exons(self):
        if(self.strand=='+'):
            return(self.exons.sort())
        else:
            return(self.exons.reverse())

    def cdsExons(self):
        retexons = []
        if(self.strand=='+'):
            for exon in sorted(self.exons):
                # full exon is CDS
                if((exon[0]>self.cdsStart) &
                   (exon[1]<=self.cdsEnd)):
                    retexons.append(exon)
                # exon contains 5' UTR
                if((self.cdsStart>exon[0]) &
                   (self.cdsStart<exon[1])):
                    retexons.append((self.cdsStart,exon[1]))
                # exon contains 3' UTR
                if((self.cdsEnd>exon[0]) &
                   (self.cdsEnd<exon[1])):
                    retexons.append((exon[0],self.cdsEnd))
            return(retexons)
        else:
            for exon in reversed(self.exons):
                # full exon is SELF.CDS
                if((exon[0]>self.cdsStart) &
                   (exon[1]<self.cdsEnd)):
                    retexons.append(exon)
                # exon contains 5' UTR
                if((self.cdsEnd>exon[0]) &
                   (self.cdsEnd<exon[1])):
                    retexons.append((exon[0],self.cdsEnd))
                # exon contains 3' UTR
                if((self.cdsStart>exon[0]) &
                   (self.cdsStart<exon[1])):
                    retexons.append((self.cdsStart,exon[1]))
            return(retexons)
            
        

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
