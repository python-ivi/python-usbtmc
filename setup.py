

# http://docs.python.org/distutils/
# http://packages.python.org/distribute/
try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name = 'python-usbtmc',
    description = 'Python USBTMC driver for controlling instruments over USB',
    version = '0.1',
    long_description = '''This Python package supports the USBTMC instrument
control protocol for controlling instruments over USB.''',
    author = 'Alex Forencich',
    author_email = 'alex@alexforencich.com',
    url = 'http://alexforencich.com/wiki/en/python-usbtmc/start',
    download_url = 'http://github.com/alexforencich/python-usbtmc/tarball/master',
    keywords = 'USB USBTMC measurement instrument',
    license = 'MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: System :: Networking',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
        ],
    packages = ['usbtmc']
)

