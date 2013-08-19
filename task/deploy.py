#!/usr/bin/env python

from paver.easy import task, needs


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass


__all__ = [
    'sdist'
]