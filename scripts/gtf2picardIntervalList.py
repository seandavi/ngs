#!/usr/bin/env python
import optparse
import logging
import sys
import ngs.formats.gtf

HEADER_INCLUDE_TAGS = ('@SQ','@HD')

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('gtf2picardIntervalList')

usage ="""usage: %prog [options] headerFile gtfFile

Takes a header that looks like a sam header (the @SQ fields only) and a gtf
file as arguments and generates a picard-format interval file.  See
http://www.broadinstitute.org/gsa/wiki/index.php/Input_files_for_the_GATK
for details."""

def main():
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-f","--feature",dest="features",
                      action="append",
                      help="""A feature matching the GTF specification, such as 'exon', 'CDS', etc.  May be specified more than once to output several feature types""")
    (opts,args)=parser.parse_args()
    if(len(args) <> 2):
        parser.error('A headerFile and gtfFile must be specified.')
    logger.info("Program arguments: %s" % (str(opts) + str(args)))
    outfile = sys.stdout
    for line in open(args[0],'r'):
        if(line.startswith(HEADER_INCLUDE_TAGS)):
            outfile.write(line)
    features = opts.features
    featurelen = len(features)
    writtenFeatures = 0
    readFeatures = 0
    for gtfrecord in ngs.formats.gtf.GTFReader(fname=args[1]).parse():
        readFeatures+=1
        if(((featurelen>0) & (gtfrecord.feature in features)) | (featurelen==0)):
            writtenFeatures+=1
            outfile.write("%s\t%d\t%d\t%s\tTarget_%d\n" % (
                gtfrecord.chromosome,
                gtfrecord.rbeg,
                gtfrecord.rend,
                gtfrecord.strand,
                readFeatures))
    outfile.close()
    logger.info("Wrote %d records out of %d records" % (writtenFeatures,readFeatures))

    
if __name__=="__main__":
    main()
