#!/usr/bin/env python

'''
simple shortcut for running nosetests via python
replacement for *.bat or *.sh wrappers
'''
import sys
import os
from copy import copy
from os.path import dirname, realpath, join
import logging
import nose
from nose.config import Config
from nose.plugins import DefaultPluginManager
extra_plugins=[]
import re

os.chdir(dirname(__file__))
sys.path.insert(0, realpath(dirname(__file__)))
sys.path.insert(0, dirname(realpath(dirname(__file__))))
argv = copy(sys.argv)
CONFIG = Config(
    files=['nose.cfg'],
    plugins=DefaultPluginManager()
)

try:
    from rednose import RedNose
except ImportError:
    pass
else:
    extra_plugins.append(RedNose())
    argv.append('--rednose')

def run_all():
    logging.debug('Running tests with arguments: %r' % sys.argv)

    nose.run_exit(
        argv=argv,
        config=CONFIG,
        addplugins=extra_plugins,
    )

class TestLoader(nose.loader.TestLoader):

    def __init__(self):
        super(self.__class__, self).__init__(config=CONFIG)

if __name__ == '__main__':
    run_all()
