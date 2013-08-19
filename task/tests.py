#!/usr/bin/env python

import os
import sys
import logging

from paver.easy import task, cmdopts, path

#
# Testing Task
#

@task
@cmdopts([
    ('verbose', 'v', 'Verbose output'),
    ('quiet', 'q', 'Minimal output'),
    ('failfast', 'f', 'Stop on first failure'),
    ('start_directory=', 's', 'Directory (or module path) to start discovery ("test" default)'),
])
def test(options):
    """ Run the functional and unit tests """
    install_dependencies(options.setup)

    logging.basicConfig(file=sys.stdout, level=logging.DEBUG, format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s")

    test_options = dict(getattr(options, 'test', {}))
    start_directory = test_options.pop('start_directory', 'test')
    
    if test_options.pop('quiet', False):
        test_options['verbosity'] = 0
        
    if test_options.pop('verbose', False):
        test_options['verbosity'] = 2

    import unittest
    runner = unittest.TextTestRunner(**test_options)
    suite = unittest.defaultTestLoader.discover(start_directory)

    if not runner.run(suite).wasSuccessful():
        raise SystemExit(False)


@task
def coverage(options):
    """ Run a test coverage report against the application """
    install_dependencies(options.setup)
    build_dist()
    run_coverage('report', show_missing=False)


@task
def html_coverage(options):
    """ Run an html test coverage report, putting the results into dist/cov_html """
    install_dependencies(options.setup)
    build_dist()
    run_coverage('html_report', directory='dist/cov_html')


@task
def xml_coverage(options):
    """ Run an xml test coverage report, putting the results into dist/coverage.xml """
    install_dependencies(options.setup)
    build_dist()
    run_coverage('xml_report', outfile='dist/coverage.xml')


def build_dist():
    """ Create the dist directory if it doesn't already exist """

    dist = path('dist')

    if dist.exists():
        return

    os.mkdir(dist)


def run_coverage(report_method, **kwargs):
    """ Run a coverage method against the test suite """

    from coverage import coverage as _coverage

    # Exclude third-party modules from coverage calculations.
    files = list(path('ticket_service').walkfiles('*.py'))

    # start the coverage recording
    c = _coverage(source=files)
    c.start()
    test()

    # create the report
    c.stop()
    getattr(c, report_method)(include=files, **kwargs)
    c.erase()


def install_dependencies(setup):
    from setuptools import dist
    distribution = dist.Distribution(attrs=setup)
    setup.install_requires.append('coverage==3.6')
    distribution.fetch_build_eggs(setup.install_requires)


__all__ = [
    'test',
    'coverage',
    'html_coverage',
    'xml_coverage'
]
