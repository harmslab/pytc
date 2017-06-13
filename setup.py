#!/usr/bin/env python3

import sys

if sys.version_info[0] < 3:
    sys.exit('Sorry, Python < 3.x is not supported')

# Try using setuptools first, if it's installed
from setuptools import setup, find_packages
from setuptools.extension import Extension
import numpy.distutils.misc_util

# set up binding polynomial C extension
ext = Extension('pytc.indiv_models.bp_ext',['src/_bp_ext.c'])

# Need to add all dependencies to setup as we go!
setup(name='pytc-fitter',
      packages=find_packages(),
      version='1.1.5',
      description="Python software package for analyzing Isothermal Titration Calorimetry data",
      long_description=open("README.rst").read(),
      author='Michael J. Harms',
      author_email='harmsm@gmail.com',
      url='https://github.com/harmslab/pytc',
      download_url='https://github.com/harmslab/pytc/tarball/1.1.5',
      zip_safe=False,
      install_requires=["matplotlib","scipy","numpy","emcee","corner"],
      package_data={"":["*.h","src/*.h"]},
      classifiers=['Programming Language :: Python'],
      ext_modules=[ext],
      include_dirs=numpy.distutils.misc_util.get_numpy_include_dirs())
