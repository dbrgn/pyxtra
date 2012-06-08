#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
try:
    import py2exe
except ImportError:
    pass

setup(name='pyxtra',
      version='1.5',
      author='Danilo Bargen, Peter Manser',
      author_email='gezuru@gmail.com',
      url='https://github.com/gwrtheyrn/pyxtra/',
      description='A small commandline utility to access the Swisscom Xtrazone SMS service',
      platforms=['Unix', 'Mac'],
      license='GPLv3',
      requires=['BeautifulSoup', 'PIL', 'mechanize', 'xlrd', 'readline', 'Tkinter'], 
      py_modules=['pyxtra', 'gorrion'],
      scripts=['pyxtra.py'],
      console=['pyxtra.py'],
      classifiers=[
          'Development Status :: Production/Stable',
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
