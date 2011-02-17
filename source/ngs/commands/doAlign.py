import csv,os,subprocess
from ngs.main import subparsers
from ngs.main import logger

def func(args):
    if((os.path.exists(args.prefix+".bam")) & (not args.overwrite)):
        return()
    # single end
    samtag="@RG\tPL:%s\tPU:%s" % (args.rg_pl,args.rg_pu)
    if(args.rg_id is not None):
        samtag+="\tID:%s" % (args.rg_id)
    if(args.rg_sm is not None):
        samtag+="\tSM:%s" % (args.rg_id)
    if(args.rg_lb is not None):
        samtag+="\tLB:%s" % (args.rg_id)
    if(args.read2 is None):
        x=subprocess.call(["novoalign -k -a -H -o SAM '%s' -c %d -d %s -f %s | samtools import %s - - | samtools sort - %s" % (samtag,args.nproc, args.novoidx, args.read1, args.faifile, args.prefix + ".tmp")],shell=True)
    # paired end
    else:
        x=subprocess.call(["novoalign -k -a -H -o SAM '%s' -c %d -d %s -f %s %s | samtools import %s - - | samtools sort - %s" % (samtag,args.nproc, args.novoidx, args.read1, args.read2, args.faifile, args.prefix + ".tmp")],shell=True)
    if(x==0):
        os.rename(args.prefix+".tmp"+".bam",args.prefix+".bam")

subparser = subparsers.add_parser(
    'doAlign',
    help="do the alignment given a set of inputs")
subparser.add_argument(
    "nproc",type=int,default=1,
    help="The number of cores to use")
subparser.add_argument(
    "novoidx",
    help="The novoalign index to use")
subparser.add_argument(
    "faifile",
    help="The .fai file to use")
subparser.add_argument(
    '-1',"--read1",
    help="read1 filename")
subparser.add_argument(
    '-2',"--read2",
    help="read2 filename")
subparser.add_argument(
    "prefix",
    help="prefix for output")
subparser.add_argument(
    "--rg_id",
    help="Read Group ID")
subparser.add_argument(
    "--rg_lb",
    help="Read Group library LB tag")
subparser.add_argument(
    "--rg_sm",
    help="Read Group sample id (source)")
subparser.add_argument(
    "--rg_pu",default="Lane",
    help="Read group platform [default Lane]")
subparser.add_argument(
    "--rg_pl",default="ILLUMINA",
    help="Read group platform [default ILLUMINA]")
subparser.add_argument(
    '-o','--overwrite',dest='overwrite',action='store_true',default=False,
    help="Overwrite output file, default is FALSE")
subparser.set_defaults(func=func)


                        
                         
