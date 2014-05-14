#!/usr/bin/env python

import os
import pkgutil
import logging
import sys

import tornado.web

from pyjojo.config import config
from pyjojo.scripts import create_collection

log = logging.getLogger(__name__)


class route(object):
    """
    decorates RequestHandlers and builds up a list of routables handlers
    
    From: https://gist.github.com/616347
    """
    
    _routes = []

    def __init__(self, uri, name=None):
        self._uri = uri
        self.name = name

    def __call__(self, _handler):
        """gets called when we class decorate"""
        
        log.info("Binding {0} to route {1}".format(_handler.__name__, self._uri))        
        name = self.name and self.name or _handler.__name__
        self._routes.append(tornado.web.url(self._uri, _handler, name=name))
        return _handler

    @classmethod
    def get_routes(self):
        return self._routes


def setup_logging():
    """ setup the logging system """
    
    base_log = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"))
    base_log.addHandler(handler)
    base_log.setLevel(logging.DEBUG)
    return handler

def create_application(debug):
    # import the handler file, this will fill out the route.get_routes() call.
    import pyjojo.handlers

    application = tornado.web.Application(
        route.get_routes(), 
        scripts=create_collection(config['directory']),
        debug=debug
    )
    
    return application
