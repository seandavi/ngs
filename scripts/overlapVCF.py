import ngs.formats.vcf
import ngs.regions
import sys

f = ngs.formats.vcf.vcfFile(sys.argv[1])
r = ngs.regions.RegionList()
j=0
for i in f.parse():
    r.add(i)
    j=j+1

x=ngs.regions.Region('chr10',80000,80001)
print j
for h in xrange(1000000):
    r.overlapCount(x)
