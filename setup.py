from setuptools import find_packages
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    name="NGS",
    version="0.1",
    cmdclass = {'build_ext': build_ext},
    packages=find_packages('source'),
    package_dir = {'':'source'},
    ext_modules = [Extension("ngs.regions", ["source/ngs/regions.pyx"])],
    scripts = ['scripts/overlapVCF.py','scripts/qseq2fastq.py','scripts/gtf2picardIntervalList.py','scripts/solexaDbQseq2fastq.py']
    )
