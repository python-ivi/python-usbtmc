=============================
Introduction to Python USBTMC
=============================

Overview
========
This Python package supports the USBTMC instrument control protocol for
controlling instruments over USB.  The implementation is pure Python and
highly portable.  

It is released under the MIT license, see LICENSE_ for more
details.

Copyright (C) 2012-2013 Alex Forencich <alex@alexforencich.com>

See also:

- `Python USBTMC home page`_
- `GitHub repository`_

.. _LICENSE: appendix.html#license
.. _`Python USBTMC home page`: http://alexforencich.com/wiki/en/python-usbtmc/start
.. _`GitHub repository`: https://github.com/alexforencich/python-usbtmc


Features
========
- Supports Python 2 and Python 3
- Pure Python
- Highly portable
- Communicates with instruments that support the USB Test and Measurement Class

Requirements
============
- Python 2 or Python 3
- PyUSB


Installation
============

To install the module for all users on the system, administrator rights (root)
are required.

From source
~~~~~~~~~~~
Download the archive, extract, and run::

    python setup.py install

Packages
~~~~~~~~
There are also packaged versions for some Linux distributions:

Arch Linux
    Python USBTMC is available under the name "python-usbtmc-git" in the AUR.

