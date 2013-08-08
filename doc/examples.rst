=====================
Python USBTMC Examples
=====================

Opening a connection
====================

Connect to an Agilent MSO7104A oscilloscope on IP address 192.168.1.104::

    >>> import usbtmc
    >>> instr =  usbtmc.Instrument(2391, 5973)
    >>> print(instr.ask("*IDN?"))
    'AGILENT TECHNOLOGIES,MSO7104A,MY********,06.16.0001'

Configuring connections
=======================

Open a connection and set the timeout::

    >>> import usbtmc
    >>> instr =  usbtmc.Instrument(2391, 5973)
    >>> instr.timeout = 60*1000
    >>> print(instr.ask("*TST?"))
    '0'
