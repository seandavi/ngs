import glob
import sys
import csv,os
dirnames = glob.glob(sys.argv[1])

firsttime=True

rows=[]
rownames=['gene_id','gene_name','location']
for d in dirnames:
    samplename = d.replace('cufflinks_','')
    rownames+=[samplename+"."+x for x in ['FPKM','FPKM_conf_lo','FPKM_conf_hi']]
    j=0
    for row in csv.DictReader(open(os.path.join(d,'genes.fpkm_tracking')),delimiter='\t'):
        if(firsttime):
            rows.append([row[x] for x in ['gene_id','gene_short_name','locus','FPKM',
                                          'FPKM_conf_lo','FPKM_conf_hi']])
        else:
            rows[j]+=[row['FPKM'],row['FPKM_conf_lo'],row['FPKM_conf_hi']]
        j+=1
    firsttime=False

print("\t".join(rownames))
for row in rows:
    print "\t".join(row)
    
