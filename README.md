# Python USBTMC Readme

For more information and updates:
http://alexforencich.com/wiki/en/python-usbtmc/start

GitHub repository:
https://github.com/alexforencich/python-usbtmc

## Introduction

Python USBTMC provides a pure Python USBTMC driver for controlling instruments
over USB.

## Installation

Extract and run

    # python setup.py install

## Usage examples

Connecting to Agilent MSO7104A via USBTMC:

    import usbtmc
    instr =  usbtmc.Instrument(2391, 5973)
    print(instr.ask("*IDN?"))
    # returns 'AGILENT TECHNOLOGIES,MSO7104A,MY********,06.16.0001'

