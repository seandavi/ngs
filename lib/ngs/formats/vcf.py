import gzip

class vcfFile:
    nextLine=None
    
    def __init__(self,fname):
        self.fname=fname
        self.fh=None
        if(fname.endswith('.gz')):
            self.fh=gzip.open(fname,'r')
        else:
            self.fh=open(fname,'r')
        self.header=[]
        line=self.fh.readline()
        while(line.startswith("#")):
            self.header.add(line.strip())
            line=self.fh.readline()
        self.nextline=line

    def parse(self):
        if(self.nextLine is not None):
            yield vcfRecord(self.nextLine)
            self.nextLine=self.fh.readline().strip()

class vcfRecord:
    def __init__(self,line):
        parts=line.split()
        self.chromosome=parts[0]
        self.position=parts[1]
        self.start=self.position-1
        self.end=self.position
        self.name=parts[2]
        self.ref=parts[3]
        self.alt=parts[4]
        self.qual=parts[5]
        self.filt=parts[6]
        self.info=parts[7]
        self.form=parts[8]
        self.samples=parts[9:]

f = gzip.open("/import/solexa1/sdavis/sequencing/NCI60/gatkVCF/2_42YM7AAXX.118_BUSTARD-2010-04-21.vcf4.gz",'r')
j=0
for i in f:
    if(not (i.startswith('#'))):
        v1 = vcfRecord(i.strip())
        j=j+1
