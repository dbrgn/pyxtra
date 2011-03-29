pyxtra
======

pyxtra is a small commandline utility to access the Swisscom Xtrazone SMS service. It is being developed for Linux- and OS X-based operating systems.

![Screenshot](https://github.com/gwrtheyrn/pyxtra/raw/master/screenshot.png)


Features
--------

- Sending SMS messages from the command line
- Access and add contacts
- Contacts tab completion (start typing and press tab to autocomplete)


Requirements
------------

- python2
- python-mechanize
- python-beautifulsoup
- python-xlrd
- python-tk
- python-imaging
- python-imaging-tk (Ubuntu/Debian users only)
- python-simplejson (for Python < 2.6 only)


Installation
------------

1. Prerequisites: You need to install python>=2.5 and tk

2. Install dependencies. If you haven't got pip installed, use `easy_install` instead.

        sudo pip install BeautifulSoup PIL mechanize xlrd

    Ubuntu users should use apt instead of pip:

        sudo apt-get install python python-tk python-mechanize python-beautifulsoup python-xlrd python-imaging python-imaging-tk

3. Install pyxtra

        sudo python setup.py install


FAQ
---

#### Q: How can I easily select the receiver from the contacts list when writing a new SMS?
A: pyxtra supports tab completion. Simply start typing a name and press the `tab` key.


Changelog
---------

v1.1 (2011-03-23)

- [add] New SMS Mode (compose SMS in looped mode), available through `n!` / `new!`
- [add] Feature to show stack traces (nice to debug)
- [bug] Fixed problem with expired sessions (Issue #7)

v1.0 (2011-03-17)

- First version released


Authors
-------

- Danilo Bargen (http://ich-wars-nicht.ch/)
- Peter Manser (http://petermanser.ch/)


License
-------

Copyright (C) 2011 Danilo Bargen, Peter Manser

pyxtra is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyxtra is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyxtra. If not, see http://www.gnu.org/licenses/.
