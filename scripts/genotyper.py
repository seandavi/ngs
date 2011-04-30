#!/usr/bin/env python
import re
from collections import defaultdict
from math import log10,pow

def phred2prob(phred):
    return(pow(10,-(float(phred)/10)))

def prob2phred(prob):
    return(-10*log10(prob))

def ascii2int(ascii):
    return ord(x)-33

class PileupRecord(object):
    indelmatchre=re.compile('\d+')
    
    def __init__(self,line):
        sline = line.strip().split("\t")
        self.chrom=sline[0]
        self.position=int(sline[1])
        self.reference=sline[2]
        self.rawbases=list(sline[4])
        self.rawquals=list(sline[5])

    def _getIndelBaseLength(self,j):
        nums=""
        k=j+1
        while self.rawbases[k] in '0123456789':
            nums+=self.rawbases[k]
            k+=1
        return(len(nums)+int(nums))
    
    def _getBaseVals(self):
        quals=[]
        bases=[]
        strands=[]
        skip=0
        i=0
        j=0
        while i<len(self.rawquals):
            nextval=self.rawbases[j]
            if(nextval=="+"):
                j+=self._getIndelBaseLength(j)+1
                continue
            if(nextval=="-"):
                j+=self._getIndelBaseLength(j)+1
                continue
            if(nextval=='^'):
                j+=2
                continue
            if(nextval=="$"):
                j+=1
                continue
            if(nextval in "<>"):
                i+=1
                j+=1
                continue
            if(nextval in 'actg,'):
                strands.append('-')
            else:
                strands.append('+')
            quals.append(ord(self.rawquals[i])-33)
            if(nextval=='.'):
                bases.append(self.reference.upper())
                i+=1
                j+=1
                continue
            if(nextval==','):
                bases.append(self.reference.upper())
                i+=1
                j+=1
                continue
            bases.append(nextval.upper())
            i+=1
            j+=1
        return(zip(bases,quals,strands))
        
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
            

if __name__=="__main__":
    import collections,sys
    f = open(sys.argv[1],'r')
    for line in f:
        x = PileupRecord(line)
        y = x._getBaseVals()
        d = dict((base,[0,0]) for base in ['N','A','C','T','G','*'])
        totbases=0
        for base in y:
            if(base[1]>13):
                totbases+=1
                if(base[2]=="+"):
                    d[base[0]][0]+=1
                else:
                    d[base[0]][1]+=1
        if(totbases==0):
            continue
        maxbase=None
        maxcount=0
        for base in d.keys():
            totbase=sum(d[base])
            if((base!=x.reference.upper()) & ((float(totbase)/totbases)>0.3) & (totbase>3)):
                if(totbase>maxcount):
                    maxbase=base
                    maxcount=totbase
        if(maxcount>0):
            print "\t".join([str(z) for z in [x.chrom,x.position,x.reference,
                                              maxbase,d[x.reference.upper()],d[maxbase]]])
        
                
