#!/usr/bin/env python

import sys
from os.path import dirname

import paver.doctools
from paver.easy import options
from paver.setuputils import setup, find_packages

# make sure the current directory is in the python import path
sys.path.append(dirname(__file__))

# default task options
options(root_dir=dirname(__file__))

# import our tasks
from task.tests import *
from task.virtualenv import *

#
# project dependencies
#

install_requires = [
    'coverage==3.6',
    'pyyaml==3.10',
    'setuptools==0.6c11',
    'tornado==3.0.1',
    'toro==0.5'
]

#
# Setuptools configuration, used to create python .eggs and such.
# See: http://bashelton.com/2009/04/setuptools-tutorial/ for a nice
# setuptools tutorial.
#

setup(
    name="pyjojo",
    version="0.1",
    
    # packaging infos
    package_data={'': []},
    packages=find_packages(exclude=['test', 'test.*', 'task', 'task.*']),
    
    # dependency infos
    install_requires=install_requires,
    
    entry_points={
        'console_scripts': [
            'pyjojo = pyjojo.util:main'
        ]
    },
    
    zip_safe=False
)