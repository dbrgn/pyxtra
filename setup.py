#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from setuptools import setup
try:
    import py2exe
except ImportError:
    pass

# Additional commands
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

# Requirements
f = open('requirements.txt', 'r')
lines = f.readlines()
requirements = [l.strip().strip('\n') for l in lines if l.strip() and not l.strip().startswith('#')]
if sys.version_info.major == 2 and sys.version_info.minor == 5:
    requirements.append('simplejson')

# Setup
setup(name='pyxtra',
      version='1.6.1',
      author='Danilo Bargen, Peter Manser',
      author_email='gezuru@gmail.com',
      url='https://github.com/dbrgn/pyxtra/',
      keywords=['sms', 'xtrazone', 'swisscom', 'communication'],
      description='A small commandline utility to access the Swisscom Xtrazone SMS service',
      long_description=open('README.rst').read(),
      platforms=['Unix', 'Mac'],
      license='GPLv3',
      requires=['BeautifulSoup', 'PIL', 'mechanize', 'xlrd', 'readline'],
      install_requires=requirements,
      provides=['pyxtra', 'gorrion'],
      py_modules=['pyxtra', 'gorrion'],
      scripts=['pyxtra.py'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: MacOS',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Communications',
          'Topic :: Internet',
          ],
     )
