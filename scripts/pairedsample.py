#!/usr/bin/env python
from ruffus import *
import argparse
import json
import subprocess
import shlex
import pysam

parser = argparse.ArgumentParser()
parser.add_argument('config',
                    help='config file name')
parser.add_argument('normalbam',
                    help='Normal bam file name')
parser.add_argument('tumorbam',
                    help='Tumor bam file name')

def run_job(cmd,shell=False):
    retval = None
    if(shell):
        retval = subprocess.call(cmd,shell=True)
    else:
        retval = subprocess.call(shlex.split(cmd))
    if(retval!=0):
        raise JobFailedException("Command failed, command string: '%s'" % cmd)
        return False
    

class JobFailedException(Exception):
    pass

opts = parser.parse_args()

with open(opts.config) as configfile:
    config=json.load(configfile)

from ngs.runners import JointSNVMix

jsm = JointSNVMix(config)

@files(opts.normalbam,opts.normalbam + '.bai')
def index_normal_bam(input,output):
    pysam.index(input)
    return

@files(opts.tumorbam,opts.tumorbam + '.bai')
def index_tumor_bam(input,output):
    pysam.index(input)
    return

@follows(index_normal_bam,index_tumor_bam)
@files([opts.normalbam,opts.tumorbam,config['reference']],[opts.tumorbam.replace('.md.recal.realigned.bam','') + ".jsm_params"])
def jsm_train(input,output):
    cmd = jsm.train(input[0],input[1],output[0])
    return run_job(cmd)

@follows(jsm_train)
@files([opts.normalbam,
        opts.tumorbam,
        opts.tumorbam.replace('.md.recal.realigned.bam','') + ".jsm_params",
        config['reference']],
       opts.tumorbam.replace('.md.recal.realigned.bam','') + ".jsm_output")
def jsm_classify(input,output):
    cmd = jsm.classify(input[0],input[1],input[2],output)
    return run_job(cmd)

@follows(index_normal_bam,index_tumor_bam)
@files([opts.normalbam,opts.tumorbam],[opts.tumorbam.replace('.md.recal.realigned.bam','.snp_callability'),opts.tumorbam.replace('.md.recal.realigned.bam','.raw.vcf')])
def unified_genotyper(input,output):
    import ngs.runners
    gatk = ngs.runners.GATK(config)
    cmd = gatk.UnifiedGenotyper(bamfiles=input,
                                metricsfile=output[0],
                                vcffile=output[1],
                                other_args=None)
    return run_job(cmd)

pipeline_run([unified_genotyper])
