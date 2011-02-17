import csv,os,subprocess
from ngs.main import subparsers
from ngs.main import logger

def func(args):
    r = csv.DictReader(open(args.samplesheet,'r'),delimiter="\t")
    for row in r:
        r1 = row['r1sequence'].replace('.tgz','.fq.gz')
        r2 = row['r2sequence'].replace('.tgz','.fq.gz')
        print("ngtools doAlign %d %s %s %s %s %s" %
              (8,'/data/sedavis/public/novoalign/hg19.index',
               '/data/sedavis/public/sequence/ucsc/hg19/genome.fa.fai',r1,r2,
               row['Lane']+"_"+row['Flowcell']))

subparser=subparsers.add_parser(
    "makeAlignCmd",
    help="generate a .cmd file for swarm submission")
subparser.add_argument(
    "samplesheet")
subparser.set_defaults(func=func)
              
        
