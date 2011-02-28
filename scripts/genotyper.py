#!/usr/bin/env python
import subprocess
from collections import defaultdict
from math import log10,pow

def phred2prob(phred):
    return(pow(10,-(float(phred)/10)))

def prob2phred(prob):
    return(-10*log10(prob))

class PileupRecord(object):
    def __init__(self,line):
        sline = line.strip().split("\t")
        self.chrom=sline[0]
        self.position=int(sline[1])
        self.reference=sline[2]
        self.rawbases=sline[4]
        self.rawquals=sline[5]


    def _getBaseVals(self):
        quals=(ord(x)-33 for x in self.rawquals)
        bases=[]
        skip=0
        for i in self.rawbases:
            if(skip>0):
                skip-=1
                continue
            if((i=='^') | (i=='$')):
                skip=1
                continue
            if(i=='.'):
                bases.append(self.reference.upper())
                continue
            if(i==','):
                bases.append(self.reference.lower())
                continue
            bases.append(i)
        return(zip(bases,quals))
        
    def baselist(self):
        try:
            return(self.bases)
        except:
            self.bases=self._getBaseVals()
            return(self.bases)

    def getBaseCounts(self):
        tmp=defaultdict(int)
        for i in self.baselist(): tmp[i[0].upper()]+=1
        return(tmp)
    

    def genotype(self,freq=(0.9999,0.0001)):
        z=tuple(self.getBaseCounts())
        print(z)
        pg00=prob2phred(freq[0]*freq[0])
        pg11=prob2phred(freq[1]*freq[1])
        pg01=prob2phred(2*freq[0]*freq[1])
        # only one allele in reads
        if(len(z)==1):
            prg00=prg11=0
            prg01=prob2phred(pow(0.5,z[1]))
            if(z[0][0]==self.reference):
                print("ref")
                prg00=sum(prob2phred(1-phred2prob(x[1])) for x in self.baselist())
                prg11=sum(x[1] for x in self.baselist())
            else:
                print("var")
                prg11=sum(prob2phred(1-phred2prob(x[1])) for x in self.baselist())
                prg00=sum(x[1] for x in self.baselist())
            pr=prob2phred(phred2prob(prg01+pg01)+
                          phred2prob(prg11+pg11)+
                          phred2prob(prg00+pg00))
            pgr00=pg00+prg00-pr
            pgr01=pg01+prg01-pr
            pgr11=pg11+prg11-pr
            print('pg00:%f\npg11%f\npg01%f\nprg00:%d\nprg11%d\nprg01%d\n' %
                  (pg00,pg11,pg01,prg00,prg11,prg01))
            return((phred2prob(pgr00),phred2prob(pgr01),phred2prob(pgr11),self.baselist()))
        # at least 2 alleles
        else:
            
        
            
        

