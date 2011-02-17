import csv,os,subprocess
from ngs.main import subparsers
from ngs.main import logger
import ngs.solexadb.model


def _doRsync(fromloc,toloc,fnameremote,fnamelocal):
    res = subprocess.call(['rsync','-avp',os.path.join(fromloc,fnameremote),
                           os.path.join(toloc,fnamelocal)])
    if(res==0):
        logger.debug('Successfully transferred %s ==> %s' % (
            os.path.join(fromloc,fnameremote),
            os.path.join(toloc,fnamelocal)))
    else:
        logger.error('Error transferring %s ==> %s' % (
            os.path.join(fromloc,fnameremote),
            os.path.join(toloc,fnamelocal)))
        


def func(args):
    r = csv.DictReader(open(args.samplesheet,'r'),delimiter="\t")
    for row in r:
        for read in ['r1sequence','r2sequence']:
            if(read=='r1sequence'):
                row[read]=row[read].replace('_1,2_','_1_')
            if(read=='r2sequence'):
                row[read]=row[read].replace('_1,2_','_2_')
            fnameremote=row[read]
            if(fnameremote=="None"):
                logger.info('Empty sequence file %s found for row:\n%s' % (read,row))
            if(args.altsuffix):
                fnameremote=fnameremote.replace('.tgz',args.altsuffix)
            fnamelocal=fnameremote # default same name
            if((int(row['index_read'])>0) & (read=='r2sequence')):
                logger.info("Found a lane with indexing, so transferring the third read and renaming to read 2")
                fnameremote=fnameremote.replace('_2_','_3_')
            _doRsync(args.fromloc,args.toloc,fnameremote,fnamelocal)

        

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
