#!/usr/bin/env python

import logging

from tornado.httpclient import HTTPClient, AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase

from pyjojo.util import create_application
from pyjojo.config import config

log = logging.getLogger(__name__)


class BaseFunctionalTest(AsyncHTTPTestCase):
    """Base class for all functional tests"""

    def get_app(self):
        # create the application
        config['directory'] = 'test/fixtures'
        return create_application(False)
    
    def get_new_ioloop(self): 
        return IOLoop.instance()
