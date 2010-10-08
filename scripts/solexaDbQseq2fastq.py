#!/usr/bin/env python
import optparse
import logging
import multiprocessing
import os
import tarfile
import gzip
import re

import ngs.solexadb.model
import ngs.solexadb.fnameutils
import ngs.formats.qseq

from sqlalchemy import and_, or_

logging.basicConfig(filename='qseq2fastq.log',level=logging.DEBUG,
                    format='[%(asctime)s %(levelname)s] %(message)s')

logger = logging.getLogger('qseq2fastq')


def outputFastq(f2,outfile,phred33=False):
    for line in f2:
        sp = line.strip().split("\t")
        qual=sp[9]
        seqstring=sp[8]
        seqstring=seqstring.replace(".","A")
        if(phred33):
            qual=ngs.formats.qseq.phred64ToStdqual(sp[9])
        outfile.write("@%s:%s:%s:%s:%s\n%s\n+\n%s\n" % (sp[0],sp[2],sp[3],sp[4],sp[5],seqstring,qual))

def worker(tfilename):
    logger.info(tfilename)
    if(os.path.exists(tfilename.replace(".tgz",".fastq.gz"))):
        logger.info("%s exists" % (tfilename.replace(".tgz",".fastq.gz")))
    else:
        tfile=tarfile.open(os.path.join("/home/analysis/Solexa/sequence",tfilename),"r:gz")
        logger.info("Getting filenames from %s" % (tfilename))
        fnames=tfile.getnames()
        qseqfiles = filter(lambda y: re.match('.*qseq.*',y),fnames)
        seqfiles = filter(lambda y: re.match('.*_seq.*',y),fnames)
        prbfiles = filter(lambda y: re.match('.*_prb.*',y),fnames)
        outfile=gzip.open(tfilename.replace(".tgz",".fastq.gz.tmp"),"w")
        logger.info("found %d qseq files, %d seq files, %d prb files in %s" % (len(qseqfiles),len(seqfiles),len(prbfiles),tfilename))
        if(len(qseqfiles)>0):
            ## deal with qseqfile
            ## should be able to just dump out to qseqfile
            j=0
            for fname in qseqfiles:
                print(fname)
                qseqfh=tfile.extractfile(fname)
                qseqfile = ngs.formats.qseq.qseqFile(fh=qseqfh)
                for qseqrec in qseqfile.parse():
                    j+=1
                    outfile.write(qseqrec.asFastqString())
            outfile.close()
            os.rename(tfilename.replace(".tgz",".fastq.gz.tmp"),
                      tfilename.replace(".tgz",".fastq.gz"))
            logger.info("%s contained %d qseq files" % (tfilename,j))           
        else:
            logger.error("%s file contains seq/prb files",tfilename)
            ## deal with seq_prb, so need split, etc.
            ## make sure same length
            ## sort both lists
            ## then run them through seq_prbfile, including split param
        tfile.close()


def main():
    sdb = ngs.solexadb.model.SolexaDB("mysql://sdavis:mic2222@amnesia.nci.nih.gov/solexa")
    smatrix = sdb.getTable("solexa_matrix")
    session = sdb.getSession()

    parser = optparse.OptionParser()
    parser.add_option("-s","--study",dest="study_id",type='int',
                      help="The study ID for which to generate fastq files")
    parser.add_option("-p","--parallel",dest="threads",type='int',
                      help="The number of workers to use in parallel")
    (opts,args)=parser.parse_args()
    sq = session.query(smatrix).filter(smatrix.c.Study_ID==opts.study_id).filter(smatrix.c.sequenceFile<>None)
    sq = sq.filter(or_(and_(smatrix.c.Read1>0,smatrix.c.Read_Direction==0),
                       and_(smatrix.c.Read2>0,smatrix.c.Read_Direction==1)))
    sq.filter(smatrix.c.Read2>0) ## Only paired-end runs, must be removed at some point
    print(sq.count())
    f = open("sampleSheet.txt",'w')
    records = set()
    for smRecord in sq:
        paired_end=1
        if(smRecord.Read2==0):
            paired_end=0
        records.add((ngs.solexadb.fnameutils.getBasename(smRecord.sequenceFile,
                                                         withReadNumber=True,
                                                         retWithReadNumber=False),
                     paired_end))
    map(lambda x: f.write("%s\t%d\n" % x),sorted(records))
    f.close()
    p = multiprocessing.Pool(opts.threads)
    smRecords=sq.all()
    #for smRecord in smRecords:
    #    worker(smRecord.sequenceFile)
    p.map(worker,(smRecord.sequenceFile for smRecord in smRecords))
    
    
main()

