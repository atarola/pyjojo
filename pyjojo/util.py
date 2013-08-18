#!/usr/bin/env python

import os
import pkgutil
import logging
import sys
from optparse import OptionParser
from pkg_resources import resource_filename

import tornado.web
import tornado.httpserver
import tornado.web
from tornado.ioloop import IOLoop

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


def command_line_options():
    """ command line configuration """
    
    parser = OptionParser(usage="usage: %prog [options] <config_file>")

    parser.add_option('-d', '--debug', action="store_true", dest="debug", default=False,
                      help="Start the application in debugging mode.")

    parser.add_option('-p', '--port', action="store", dest="port", default=3000,
                      help="Set the port to listen to on startup.")

    parser.add_option('-a', '--address', action ="store", dest="address", default=None,
                      help="Set the address to listen to on startup. Can be a hostname or an IPv4/v6 address.")
    
    parser.add_option('--dir', action="store", dest="directory", default="/srv/pyjojo",
                      help="sqlalchemy url for database")

    options, args = parser.parse_args()

    if len(args) >= 1:
        config.load_file(args[0])
        
    config['directory'] = options.directory

    return options
    

def setup_logging():
    """ setup the logging system """
    
    base_log = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"))
    base_log.addHandler(handler)
    base_log.setLevel(logging.DEBUG)
    return handler


def main():
    """ entry point for the application """
    
    root = os.path.dirname(__file__)
        
    # get the command line options
    options = command_line_options()
    handler = setup_logging()

    # setup the application
    log.info("Setting up the application")
    
    # import the handler file.  this will fill out the route object.
    import pyjojo.handlers
    
    application = tornado.web.Application(
            route.get_routes(), 
            debug=options.debug
        )
    
    application.listen(options.port, options.address)
    application.settings['scripts'] = create_collection(config['directory'])

    # start the ioloop
    log.info("Starting the IOLoop")
    IOLoop.instance().start()
