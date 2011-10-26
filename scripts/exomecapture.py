#!/usr/bin/env python
from ruffus import *
import sys
import argparse
import subprocess
import os
import json
import shlex

def run_job(cmd):
    retval = subprocess.call(shlex.split(cmd))
    if(retval!=0):
        raise JobFailedException("Command failed, command string: '%s'" % cmd)
        return False
    

class JobFailedException(Exception):
    pass

parser = argparse.ArgumentParser()
parser.add_argument('config')
parser.add_argument('fname')
opts=parser.parse_args()
fname=opts.fname
fname1 = fname.replace('.bam','.md.bam')
fname2 = fname1.replace('.md.bam','.md.realigned.bam')
with open(opts.config) as configfile:
    config=json.load(configfile)

@transform(fname,suffix('.bam'),'.bam.bai')
def index_bam(input,output):
    cmd = 'samtools index %s' % input
    return run_job(cmd)

@transform(fname,suffix('.bam'),add_inputs(r'\1.bam.bai'),['.md.bam','.dupmetrics'])
@follows(index_bam)
def mark_duplicates(input,output):
    cmd = """%s -jar /usr/local/picard/MarkDuplicates.jar I=%s O=%s M=%s AS=true VALIDATION_STRINGENCY=SILENT CREATE_INDEX=true""" % (config['paths']['java'],input[0],output[0],output[1])
    return run_job(cmd)

@transform(fname1,suffix('.md.bam'),'.md.realign.intervals')
@follows(mark_duplicates)
def realign_target_create(input,output):
    cmd = """%s -Xmx4g -jar /usr/local/GATK/GenomeAnalysisTK.jar -T RealignerTargetCreator -R /data/sedavis/public/sequences/ucsc/hg19/genome.fa -I %s -o %s --known /data/sedavis/public/GATK/dbsnp_132.hg19.reforder.vcf.gz""" % (config['paths']['java'],input,output)
    return run_job(cmd)

@transform(fname1,suffix('.md.bam'),add_inputs(r'\1.md.realign.intervals'),'.md.realigned.bam')
@follows(realign_target_create)
def indel_realign(input,output):
    cmd = """%s -Xmx4g -jar /usr/local/GATK/GenomeAnalysisTK.jar -T IndelRealigner -R /data/sedavis/public/sequences/ucsc/hg19/genome.fa -I %s --targetIntervals %s -o %s --known /data/sedavis/public/GATK/dbsnp_132.hg19.reforder.vcf.gz""" % (config['paths']['java'],input[0],input[1],output)
    return run_job(cmd)

@transform(fname2,suffix('.md.realigned.bam'),'.md.recal_data.csv')
@follows(indel_realign)
def count_covariates(input,output):
    cmd = """/usr/local/bin/java64 -Xmx4g -jar /usr/local/GATK/GenomeAnalysisTK.jar -T CountCovariates -knownSites /data/sedavis/public/GATK/dbsnp_132.hg19.reforder.vcf.gz -R /data/sedavis/public/sequences/ucsc/hg19/genome.fa --default_platform illumina -I %s -recal_file %s -cov ReadGroupCovariate -cov QualityScoreCovariate -cov CycleCovariate -cov DinucCovariate""" % (input,output)
    return run_job(cmd)
    

@transform(fname2,suffix('.md.realigned.bam'),add_inputs(r'\1.md.recal_data.csv'),'.md.recal.realigned.bam')
@follows(count_covariates)
def quality_recalibrate(input,output):
    cmd = """/usr/local/bin/java64 -Xmx4g -jar /usr/local/GATK/GenomeAnalysisTK.jar -T TableRecalibration --default_platform illumina --knownSites /data/sedavis/public/GATK/dbsnp_132.hg19.reforder.vcf.gz -R /data/sedavis/public/sequences/ucsc/hg19/genome.fa -o %s -I %s --recal_file %s""" % (output,input[0],input[1])
    return run_job(cmd)


import logging
try:
    os.mkdir("log")
except OSError:
    pass
formatter = logging.Formatter('%(asctime)s:%(levelname)s %(message)s')
logger = logging.getLogger("exomepp:%s" % (fname))
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join("log",fname + ".log"))
handler.setFormatter(formatter)
logger.addHandler(handler)


pipeline_run([quality_recalibrate],verbose=5,logger=logger,log_exceptions=True,
             exceptions_terminate_immediately = True)
## pipeline_printout_graph(open('flowchart.svg','w'),
##                         'svg',
##                         [quality_recalibrate]
##                         )
