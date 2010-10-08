#!/usr/bin/env python
import optparse
import collections
import operator

import ngs.formats.fastq

def sortHash(h):
    return sorted(h.iteritems(),key=operator.itemgetter(1),reverse=True)

def main():
    parser = optparse.OptionParser(usage="Usage: %prog [options] fastqfile")
    parser.add_option('-k','--kmer',dest='kmer',
                      type="int",help="The size of the kmer to generate")
    (opts,args) = parser.parse_args()
    if(len(args)!=1):
        sys.stderr.write('A fastq file name must be specified')
        exit(1)
    seqcount = collections.defaultdict(int)
    x = ngs.formats.fastq.ParseFastQ(args[0])
    for fastqRecord in x:
        seqcount[fastqRecord[1][0:(opts.kmer+1)]]+=1
    for k,v in sortHash(seqcount):
        print("%s\t%d" % (k,v))

        

main()
