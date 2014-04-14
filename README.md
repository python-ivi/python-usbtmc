# Python USBTMC Readme

For more information and updates:
http://alexforencich.com/wiki/en/python-usbtmc/start

GitHub repository:
https://github.com/python-ivi/python-usbtmc

Google group:
https://groups.google.com/d/forum/python-ivi

## Introduction

Python USBTMC provides a pure Python USBTMC driver for controlling instruments
over USB.

## Requirements

* Python 2 or Python 3
* PyUSB

## Installation

Extract and run

    # python setup.py install

## Configuring udev

If you cannot access your device without running your script as root, then you
may need to create a udev rule to properly set the permissions of the device.
First, connect your device and run lsusb.  Find the vendor and product IDs.
Then, create a file /etc/udev/rules.d/usbtmc.rules with the following content:

    # USBTMC instruments
    
    # Agilent MSO7104
    SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="0957", ATTRS{idProduct}=="1755", GROUP="usbtmc", MODE="0660"

substituting the correct idVendor and idProduct from lsusb.  You will also need
to create the usbtmc group and add yourself to it or substitute another group
of your choosing.  It seems that udev does not allow 0666 rules, usually
overriding the mode to 0664, so you will need to be a member of the associated
group to use the device.

If you want to put the kernel usbtmc device in the same group, add the
following content to the usbtmc.rules file as well.  This is optional as
Python USBTMC bypasses and disconnects the kernel usbtmc driver and the device
will actually disappear from /dev when Python USBTMC connects.

    # Devices
    KERNEL=="usbtmc/*",       MODE="0660", GROUP="usbtmc"
    KERNEL=="usbtmc[0-9]*",   MODE="0660", GROUP="usbtmc"

## Windows setup

To use Python USBTMC in Windows, PyUSB and libusb are required.  They can be
downloaded from:

* http://sourceforge.net/projects/pyusb/
* http://www.libusb.org/wiki/libusb-win32

An INF file will also need to be created in order to use devices with libusb.
Without a properly set up INF file, Python USBTMC will not be able to locate
the device.  There are instructions on the libusb page for how to generate the
INF file.  

## Usage examples

Connecting to Agilent MSO7104A via USBTMC:

    import usbtmc
    instr =  usbtmc.Instrument(2391, 5973)
    print(instr.ask("*IDN?"))
    # returns 'AGILENT TECHNOLOGIES,MSO7104A,MY********,06.16.0001'

When multiple instruments are connected they can be identified by serial number:

    import usbtmc
    instr =  usbtmc.Instrument(2391, 5973, 'MY********')
    print(instr.ask("*IDN?"))
    # returns 'AGILENT TECHNOLOGIES,MSO7104A,MY********,06.16.0001'

It is also possible to connect with VISA resource strings like so:

    import usbtmc
    instr =  usbtmc.Instrument("USB::0x0957::0x1755::INSTR")
    print(instr.ask("*IDN?"))
    # returns 'AGILENT TECHNOLOGIES,MSO7104A,MY********,06.16.0001'

and:

    import usbtmc
    instr =  usbtmc.Instrument("USB::0x0957::0x1755::MY********::INSTR")
    print(instr.ask("*IDN?"))
    # returns 'AGILENT TECHNOLOGIES,MSO7104A,MY********,06.16.0001'

