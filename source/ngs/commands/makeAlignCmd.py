import csv,os,subprocess
from ngs.main import subparsers
from ngs.main import logger

def func(args):
    r = csv.DictReader(open(args.samplesheet,'r'),delimiter="\t")
    for row in r:
        r1 = row['r1sequence'].replace('.tgz','.fq.gz')
        r1 = r1.replace('_1,2_','_1_')
        r2 = row['r2sequence'].replace('.tgz','.fq.gz')
        r2 = r2.replace('_1,2_','_2_')
        if(r2=='None'):
            print("ngtools doAlign -1 %s --rg_id '%s' --rg_lb '%s' --rg_sm '%s' %d %s %s %s" %
                  (r1,row['Lane']+"_"+row['Flowcell'],
                   row['library_name'],row['source_name'],
                   8,'/data/sedavis/public/novoalign/hg18.index',
                   '/data/sedavis/public/sequence/ucsc/hg18/genome.fa.fai',
                   row['Lane']+"_"+row['Flowcell']))
        else:
            print("ngtools doAlign -1 %s -2 %s --rg_id '%s' --rg_lb '%s' --rg_sm '%s' %d %s %s %s" %
                  (r1,r2,row['Lane']+"_"+row['Flowcell'],
                   row['library_name'],row['source_name'],
                   8,'/data/sedavis/public/novoalign/hg18.index',
                   '/data/sedavis/public/sequence/ucsc/hg18/genome.fa.fai',
                   row['Lane']+"_"+row['Flowcell']))


subparser=subparsers.add_parser(
    "makeAlignCmd",
    help="generate a .cmd file for swarm submission.  Output is simply to stdout.")
subparser.add_argument(
    "samplesheet")
subparser.add_argument(
    'faifile')
subparser.add_argument(
    'novoindex')
subparser.set_defaults(func=func)
              
        
