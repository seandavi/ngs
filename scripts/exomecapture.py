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
fname3 = fname2.replace('.md.realigned.bam','.md.recal.realigned.bam')
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
    cmd = """/usr/local/bin/java64 -Xmx4g -jar /usr/local/GATK/GenomeAnalysisTK.jar -T CountCovariates --knownSites /data/sedavis/public/GATK/dbsnp_132.hg19.reforder.vcf.gz -R /data/sedavis/public/sequences/ucsc/hg19/genome.fa --default_platform illumina -I %s --recal_file %s -cov ReadGroupCovariate -cov QualityScoreCovariate -cov CycleCovariate -cov DinucCovariate""" % (input,output)
    return run_job(cmd)
    

@transform(fname2,suffix('.md.realigned.bam'),add_inputs(r'\1.md.recal_data.csv'),'.md.recal.realigned.bam')
@follows(count_covariates)
def quality_recalibrate(input,output):
    cmd = """/usr/local/bin/java64 -Xmx4g -jar /usr/local/GATK/GenomeAnalysisTK.jar -T TableRecalibration --default_platform illumina -R /data/sedavis/public/sequences/ucsc/hg19/genome.fa -o %s -I %s --recal_file %s""" % (output,input[0],input[1])
    return run_job(cmd)

@transform(fname3,suffix('.md.recal.realigned.bam'),['.insert_histogram','.insert_size.txt'])
@follows(quality_recalibrate)
def insert_size_metrics(input,output):
    cmd = """/usr/local/bin/java64 -Xmx4g -jar /usr/local/picard/CollectInsertSizeMetrics.jar VALIDATION_STRINGENCY=SILENT REFERENCE_SEQUENCE=/data/sedavis/public/sequences/ucsc/hg19/genome.fa ASSUME_SORTED=true HISTOGRAM_FILE=%s INPUT=%s OUTPUT=%s""" % (output[0],input,output[1])
    return run_job(cmd)

## @transform(fname3,suffix('.md.recal.realigned.bam'),['.gc_bias_summary.txt','.gc_bias.txt','.gc_chart'])
## @follows(quality_recalibrate)
## def gc_bias_metrics(input,output):
##     cmd = """/usr/local/bin/java64 -Xmx4g -jar /usr/local/picard/CollectGcBiasMetrics.jar VALIDATION_STRINGENCY=SILENT REFERENCE_SEQUENCE=/data/sedavis/public/sequences/ucsc/hg19/genome.fa INPUT=%s OUTPUT=%s CHART_OUTPUT=%s SUMMARY_OUTPUT=%s""" % (input,output[1],output[2],output[1])
##     return run_job(cmd)

@follows(quality_recalibrate)
@transform(fname3,suffix('.md.recal.realigned.bam'),add_inputs('/data/sedavis/sequencing/capture/SureSelect_All_Exon_50mb_with_annotation_hg19.interval_list','/data/sedavis/sequencing/capture/refgene.cdsonly.hg19.interval_list'),['.hsmetrics','.target.hsmetrics'])
def hs_metrics(input,output):
    cmd = """/usr/local/bin/java64 -Xmx4g -jar /usr/local/picard/CalculateHsMetrics.jar VALIDATION_STRINGENCY=SILENT REFERENCE_SEQUENCE=/data/sedavis/public/sequences/ucsc/hg19/genome.fa INPUT=%s BAIT_INTERVALS=%s TARGET_INTERVALS=%s OUTPUT=%s PER_TARGET_COVERAGE=%s """ % (input[0],input[1],input[2],output[0],output[1])
    return run_job(cmd)

@post_task(touch_file(os.path.join('log',fname3 + ".finished")))
@follows(hs_metrics,insert_size_metrics)
def finalize():
    pass




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


#pipeline_printout_graph(open('flowchart.svg','w'),
#                         'svg',
#                         [final_task]
#                         )
pipeline_run([finalize],verbose=5,logger=logger,log_exceptions=True,
             exceptions_terminate_immediately = True)
