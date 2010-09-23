from setuptools import setup, find_packages
setup(
    name="NGS",
    version="0.1",
    packages=find_packages('lib'),
    package_dir = {'':'lib'},
    scripts = ['scripts/overlapVCF.py','scripts/qseq2fastq.py'],
    )
