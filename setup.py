from setuptools import setup, find_packages
setup(
    name="NGS",
    version="0.1",
    packages=find_packages('source'),
    package_dir = {'':'source'},
    scripts = ['scripts/overlapVCF.py','scripts/qseq2fastq.py','scripts/gtf2picardIntervalList.py']
    )
