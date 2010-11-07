from setuptools import find_packages
from distutils.core import setup
from distutils.extension import Extension

setup(
    name="NGS",
    version="0.1",
    packages=find_packages('.'),
    package_dir = {'':'.'},
    install_requires=[
        "pysam>=0.3.1",
        "Cython", # This is required by pysam
        "bx-python",
        "pyfasta"
    ],
    scripts = ['scripts/overlapVCF.py',
               'scripts/qseq2fastq.py',
               'scripts/gtf2picardIntervalList.py',
               'scripts/solexaDbQseq2fastq.py',
               'scripts/annotate_variants.py']
    )
