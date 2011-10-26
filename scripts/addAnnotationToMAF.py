import argparse
import gzip
import csv
import sys
import ngs.genomicintervals
import ngs.formats.maf

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--colname",
                        help="The literal column name to include in the new MAF file")
    parser.add_argument('-n','--column',
                        help="The column from the annotation file to include as the value in the resulting MAF file, defaults to the column after the 'end' column, or column 4 for a bed file")
    parser.add_argument("mafname",
                        help="name of the MAF file, and may be gzipped (ending in .gz) or '-' for stdin")
    parser.add_argument("annotationname",
                        help="name of the annotation file, and may be gzipped (ending in .gz)")
    args=parser.parse_args()
    geneexpr = {}
    fh = None
    if(args.annotationname.endswith(".gz")):
        fh = gzip.GzipFile(args.annotationname)
    else:
        fh = open(args.annotationname)
    reader=csv.reader(fh,delimiter="\t")
    firsttime=True
    skip=0
    annotationvalcolumn=skip+3
    it=ngs.genomicintervals.GenomicIntervalTree()
        
    for row in reader:
        if(firsttime):
            if(row[0].startswith('chr')):
                skip=0
            else:
                skip=1
            firsttime=False
            if(args.column is None):
                annotationvalcolumn=skip+3
            else:
                annotationvalcolumn=int(args.column)

        it.add_interval(ngs.genomicintervals.GenomicInterval(chrom=row[skip],
                                        start=int(row[skip+1]),
                                        end=int(row[skip+2]),
                                        value=row[annotationvalcolumn]))
    colname = args.annotationname
    if(args.colname is not None):
        colname=args.colname
    maffile=None
    if(args.mafname=='-'):
        maffile = ngs.formats.maf.MAFFile(sys.stdin)
    else:
        maffile = ngs.formats.maf.MAFFile(args.mafname)
    headers = maffile.reader.fieldnames
    headers.append(colname)
    print("\t".join(headers))
    for mafrecord in maffile:
        mafrecord[colname]=";".join([x.value for x in it.find(mafrecord['Chromosome'],
                                                              mafrecord['Start_position'],
                                                              mafrecord['End_position'])])
        print("\t".join([str(mafrecord[x]) for x in headers]))

if __name__=="__main__":
    main()
