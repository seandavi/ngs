import csv,os,subprocess
from ngs.main import subparsers
from ngs.main import logger
import ngs.solexadb.model


def _doRsync(fromloc,toloc,fname):
    res = subprocess.call(['rsync','-avp',os.path.join(fromloc,fname),
                           os.path.join(toloc,fname)])
    if(res==0):
        logger.debug('Successfully transferred %s ==> %s' % (
            os.path.join(fromloc,fname),
            os.path.join(toloc,fname)))
    else:
        logger.error('Error transferring %s ==> %s' % (
            os.path.join(fromloc,fname),
            os.path.join(toloc,fname)))
        


def func(args):
    r = csv.DictReader(open(args.samplesheet,'r'),delimiter="\t")
    for row in r:
        for read in ['r1sequence','r2sequence']:
            fname=row[read]
            if(fname is ""):
                logger.error('Empty sequence file %s found for row:\n%s' % (read,row))
            if(args.altsuffix):
                fname=fname.replace('.tgz',args.altsuffix)
            _doRsync(args.fromloc,args.toloc,fname)
            
        

subparser = subparsers.add_parser(
    'getsequence',
    help="Given a sample sheet in standard form, rsync the files from one location to another")
subparser.add_argument(
    "-f","--from-location",required=True,dest='fromloc',
    help="A uri (without filename) as recognized by rsync, such as username@example.com:/path/to/sequencefiles")
subparser.add_argument(
    "-t","--to-location",dest="toloc",default='.',
    help="A uri (without filename) as recognized by rsync, such as username@example.com:/path/to/sequencefiles or '.' [default '.']")
subparser.add_argument(
    "-a","--alternative-suffix",dest="altsuffix",default='.',
    help="The sequence files have a suffix '.tgz' that could be replaced with another suffix, for example '.fq.gz' to get the fastq files.  Specify the alternate suffix here.")
subparser.add_argument(
    "samplesheet",
    help="The name of the samplesheet file from which to pull the sequence names")

subparser.set_defaults(func=func)
