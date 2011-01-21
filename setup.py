from setuptools import find_packages
from distutils.core import setup
from distutils.extension import Extension

setup(
    name="NGS",
    version="0.1",
    packages=find_packages('source'),
    package_dir = {'':'source'},
        install_requires=[
        # "pysam>=0.3.0",
        # "Cython", # This is required by pysam
        "bx-python"
    ],
    scripts = ['scripts/overlapVCF.py',
               'scripts/qseq2fastq.py',
               'scripts/gsnapSplicePrep.py',
               'scripts/gtf2picardIntervalList.py',
               'scripts/solexaDbQseq2fastq.py',
               'scripts/ngCGH.py',
               'scripts/annotate_variants.py',
               'scripts/cg_somaticcalls2annovar.py',
               'scripts/readLengthHistogram.py']
    )
