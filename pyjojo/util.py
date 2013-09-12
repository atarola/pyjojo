#!/usr/bin/env python

import os
import pkgutil
import logging
import sys
from optparse import OptionParser, IndentedHelpFormatter
from pkg_resources import resource_filename

import tornado.web
import tornado.httpserver
import tornado.web
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

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


class PlainHelpFormatter(IndentedHelpFormatter): 
    def format_description(self, description):
        if description:
            return description + "\n"
        else:
            return ""


def command_line_options():
    """ command line configuration """
    
    parser = OptionParser(usage="usage: %prog [options] <htpasswd>")
    
    parser.formatter = PlainHelpFormatter()
    parser.description = """Expose a directory of bash scripts as an API.

Note: This application gives you plenty of bullets to shoot yourself in the 
foot!  Please use the SSH config options, give a password file, and either 
whitelist access to it via a firewall or keep it in a private network.

You can use the apache htpasswd utility to create your htpasswd files.  If
you do, I recommend passing the -d flag, forcing the encryption type pyjojo
recognises."""
    
    parser.add_option('-d', '--debug', action="store_true", dest="debug", default=False,
                      help="Start the application in debugging mode.")
    
    parser.add_option('-p', '--port', action="store", dest="port", default=3000,
                      help="Set the port to listen to on startup.")
    
    parser.add_option('-a', '--address', action ="store", dest="address", default=None,
                      help="Set the address to listen to on startup. Can be a hostname or an IPv4/v6 address.")
    
    parser.add_option('--dir', action="store", dest="directory", default="/srv/pyjojo",
                      help="Base directory to parse the scripts out of")
    
    parser.add_option('-c', '--certfile', action="store", dest="certfile", default=None,
                      help="SSL Certificate File")
    
    parser.add_option('-k', '--keyfile', action="store", dest="keyfile", default=None,
                      help="SSL Private Key File")

    options, args = parser.parse_args()

    # TODO: only do this if they specify the ssl certfile and keyfile
    if len(args) >= 1:
        config['passwords'] = parse_password_file(args[0])
    else:
        config['passwords'] = None
        
    config['directory'] = options.directory

    return options
    

def parse_password_file(file_name):
    """ parse the apache password file into usernames and passwords """
    passwords = {}
    
    for line in open(file_name, 'r'):
        username, password = line.split(':')
        passwords[username] = password.strip()
    
    return passwords


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

    # import the handler file, this will fill out the route.get_routes() call.
    import pyjojo.handlers

    # setup the application
    log.info("Setting up the application")
    
    application = tornado.web.Application(
        route.get_routes(), 
        scripts=create_collection(config['directory']),
        debug=options.debug
    )
    
    # if we're passed a certfile and keyfile, start the app as an HTTPS server, 
    # otherwise use HTTP. 
    if options.certfile and options.keyfile:        
        server = HTTPServer(application, ssl_options={
            "certfile": options.certfile,
            "keyfile": options.keyfile
        })
    else:
        log.warn("Application is running in HTTP mode, this is insecure.  Pass in the --certfile and --keyfile to use SSL.")
        server = HTTPServer(application)

    # set the server port and fork subprocesses to run
    server.bind(options.port, options.address)
    server.start(1)
    
    # start the ioloop
    log.info("Starting the IOLoop")
    IOLoop.instance().start()
