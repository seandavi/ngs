from ngs.main import subparsers
from ngs.main import logger
import ConfigParser
import csv
import subprocess
import os

def func(args):
    config = ConfigParser.RawConfigParser()
    config.read(args.configfile)
    picardbase = config.get('picard','basedir')
    gatkbase   = config.get('GATK','basedir')
    gatkref    = config.get('GATK','reference')
    gatkdbsnp  = config.get('GATK','dbsnp')
    markdups = subprocess.call(["java64 -Xmx4g -jar %s AS=true VALIDATION_STRINGENCY=SILENT O=%s I=%s M=%s " %
                                (os.path.join(picardbase,"MarkDuplicates.jar"),
                                 args.infilename.replace(args.insuffix,'.dupsmarked.bam'),
                                 args.infilename,
                                 args.infilename.replace(args.insuffix,'.dupmetrics'))],
                               shell=True)
    if(args.recalibrate==True):
        countcov = subprocess.call(["""java64 -Xmx4g -jar %s/GenomeAnalysisTK.jar \
          -l INFO \
          -R %s \
          --DBSNP %s \
          -I %s \
          -U \
          --default_platform Illumina \
          -T CountCovariates \
           -cov ReadGroupCovariate \
           -cov QualityScoreCovariate \
           -cov CycleCovariate \
           -cov DinucCovariate \
          --default_read_group %s \
           -recalFile %s
        """ % (gatkbase,
               gatkref,
               gatkdbsnp,
               args.infilename.replace(args.insuffix,'.dupsmarked.bam'),       
               args.infilename.replace(args.insuffix,''),       
               args.infilename.replace(args.insuffix,'.recal.csv'))],shell=True)
        tabrecal = subprocess.call(["""java64 -Xmx4g -jar %s/GenomeAnalysisTK.jar \
          -T TableRecalibration \
          -l INFO \
          -U \
          -R %s \
          -I %s \
          --default_platform Illumina \
          --default_read_group %s \
           --out %s \
           -recalFile %s
        """ % (gatkbase,
               gatkref,
               args.infilename.replace(args.insuffix,'.dupsmarked.bam'),       
               args.infilename.replace(args.insuffix,''),       
               args.infilename.replace(args.insuffix,args.outsuffix),       
           args.infilename.replace(args.insuffix,'.recal.csv'))],shell=True)
    if(args.realign):
        targetcreator=subprocess.call(["java64 -Xmx4g -jar %s/GenomeAnalysisTK.jar \
        -T RealignerTargetCreator \
        -R %s \
        -o %s.intervals \
        -I %s \
        -U \
        -D %s" % (gatkbase,
                  gatkref,
                  args.infilename.replace(args.insuffix,''),
                  args.infilename.replace(args.insuffix,'.dupsmarked.bam'),
                  gatkdbsnp)],shell=True)
        realigner=subprocess.call(["java64 -Xmx4g -jar %s/GenomeAnalysisTK.jar \
        -T IndelRealigner\
        -R %s \
        -targetIntervals %s.intervals \
        -I %s \
        -D %s \
        -U \
        -o %s" % (gatkbase,
                  gatkref,
                  args.infilename.replace(args.insuffix,''),
                  args.infilename.replace(args.insuffix,'.dupsmarked.bam'),
                  gatkdbsnp,
                  args.infilename.replace(args.insuffix,'.processed.bam')
                  )],shell=True)
                                          
subparser=subparsers.add_parser(
    "exomePostProcess",
    help="Postprocess a single lane of exome data, including duplicate marking and quality recalibration.  No indel realignment is done as BAQ is expected downstream")
subparser.add_argument(
    "infilename",
    help="The input filename")
subparser.add_argument(
    "-o","--out-suffix",dest="outsuffix",default=".processed.bam",
    help="The output suffix name, to be appended after stripping in-suffix from the input filename [default: .processed.bam]")
subparser.add_argument(
    "-i","--in-suffix",dest='insuffix',default=".bam",
    help="The input file suffix, to be stripped before appending the outsuffix, [default: .bam]")
subparser.add_argument(
    "-j","--javaDir",dest="javadir",default="/data/sedavis/usr/local/jars/",
    help="base directory for java jar files")
subparser.add_argument(
    "-c","--configfile",dest="configfile",default="ngs.conf",
    help="config file for paths, default variables, etc.")
subparser.add_argument(
    "-r","--recalibrate",dest="recalibrate",action="store_true",default=False,
    help="Perform table recalibration, default is to NOT do it")
subparser.add_argument(
    "-a","--realign",dest="realign",action="store_true",default=False,
    help="Perform indel realignment, default is to NOT do it")
subparser.set_defaults(func=func)
