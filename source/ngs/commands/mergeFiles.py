from ngs.main import subparsers
from ngs.main import logger
import ConfigParser
import csv

def func(args):
    r = csv.DictReader(open(args.samplesheet,'r'),delimiter="\t")
    d = {}
    for row in r:
        if((args.sampletype is not None) & (row['sample_type'].strip()!=args.sampletype)):
           continue
        try:
            d[row['source_name'].strip()].append(row)
        except KeyError:
            d[row['source_name'].strip()]=[]
            d[row['source_name'].strip()].append(row)

    for k,v in d.items():
        if(len(v)>1):
            print('java -jar /data/sedavis/usr/local/jars/picard/MergeSamFiles.jar ASSUME_SORTED=true OUTPUT=%s %s' %
                  ("'" + k + ".bam'",
                   " ".join(["INPUT='" + x['Lane'] + "_" + x['Flowcell'] + args.suffix + "'" for x in v])))
        else:
            print("ln -s %s %s" %
                  (" ".join(["'" + x['Lane'] + "_" + x['Flowcell'] + args.suffix + "'" for x in v]),
                  "'" + k + ".bam'"))


subparser=subparsers.add_parser(
    "makeMergeCmd",
    help="Use this to merge lanes of data into a single file, based on source_name in samplesheet")
subparser.add_argument(
    'samplesheet',
    help="The samplesheet for the project")
subparser.add_argument(
    "-s","--suffix",dest="suffix",default=".bam",
    help="Suffix to append to the standard lane_flowcell nomenclature for the input bam files (eg., 'recal.sorted.bam' or '.bam')")
subparser.add_argument(
    "-t","--sampleType",dest="sampletype",
    help="Limit the type of sample to deal with (Genomic DNA, mRNA, etc.) from the 'sample_type' column in the samplesheet")
subparser.set_defaults(func=func)
