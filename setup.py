#!/usr/bin/env python

from setuptools import setup, find_packages

#
# project dependencies
#

install_requires = [
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
    # metadata
    name="pyjojo",
    version="0.5",
    author="Anthony Tarola",
    author_email="anthony.tarola@gmail.com",
    description="Expose a set of shell scripts as an API.",
    url="https://github.com/atarola/pyjojo",
    
    # packaging info
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=install_requires,
    
    entry_points={
        'console_scripts': [
            'pyjojo = pyjojo.util:main'
        ]
    },
    
    zip_safe=False
)
