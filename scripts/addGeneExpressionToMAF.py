import argparse
import csv
import gzip

import ngs.formats.maf

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mafname",
                        help="name of the MAF file, and may be gzipped (ending in .gz)")
    parser.add_argument("cufflinksfile",
                        help="name of the cufflinks gene.fpkm_tracking file, and may be gzipped (ending in .gz)")
    args=parser.parse_args()
    maffile = ngs.formats.maf.MAFFile(args.mafname)
    geneexpr = {}
    fh = None
    if(args.cufflinksfile.endswith(".gz")):
        fh = gzip.GzipFile(args.cufflinksfile)
    else:
        fh = open(args.cufflinksfile)
    reader=csv.DictReader(fh,delimiter="\t")
    for row in reader:
        geneexpr[row['gene_short_name']]=[row['FPKM'],row['FPKM_conf_lo'],row['FPKM_conf_hi']]
    headers = maffile.reader.fieldnames
    headers+=['FPKM','FPKM_conf_lo','FPKM_conf_hi']
    print("\t".join(headers))
    for mafrecord in maffile:
        genesymbol = mafrecord['Hugo_Symbol'].split(';')
        mafrecord['FPKM']=''
        mafrecord['FPKM_conf_lo']=''
        mafrecord['FPKM_conf_hi']=''
        if(len(genesymbol)>0):
            if(genesymbol[0] in geneexpr):
                genespecexpr = geneexpr[genesymbol[0]]
                mafrecord['FPKM']=genespecexpr[0]
                mafrecord['FPKM_conf_lo']=genespecexpr[1]
                mafrecord['FPKM_conf_hi']=genespecexpr[2]
        print("\t".join([str(mafrecord[x]) for x in headers]))
        
    
if __name__=='__main__':
    main()
