#!/usr/bin/env python

import os
import shutil
import sys

from paver.easy import task, needs, Bunch, options, call_task, sh

# default options
options(
    bootstrap=Bunch(bootstrap_dir="."),
    virtualenv=Bunch()
)


@task
def destroy_virtualenv(options):
    """ destroy the virtualenv """

    for d in ['build', 'dist', 'bin', 'include', 'lib', 'pyjojo.egg-info']:
        if os.path.exists(os.path.join(options.root_dir, d)):
            shutil.rmtree(d)

    for f in ['bootstrap.py', '.Python']:
        if os.path.exists(os.path.join(options.root_dir, f)):
            os.remove(f)


@task
@needs('destroy_virtualenv')
def create_virtualenv(options):
    """ create virtual environment """
    # TODO: use paver options

    try:
        import virtualenv
    except ImportError as e:
        raise RuntimeError("virtualenv is needed for bootstrap")

    options.virtualenv.dest_dir = '.'
    options.virtualenv.no_site_packages = True
    options.virtualenv.paver_command_line = "develop"
    call_task('paver.virtual.bootstrap')
    sh('%s %s' % (sys.executable, 'bootstrap.py'))


__all__ = [
    'create_virtualenv',
    'destroy_virtualenv'
]
