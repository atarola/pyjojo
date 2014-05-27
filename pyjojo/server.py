#!/usr/bin/env python

import logging

from tornado.ioloop import IOLoop

from pyjojo.options import command_line_options
from pyjojo.util import setup_logging, create_application
from pyjojo.servers import http_server, https_server, unix_socket_server

log = logging.getLogger(__name__)

def main():
    """ entry point for the application """

    # get the command line options
    options = command_line_options()
    setup_logging()

    # setup the application
    log.info("Setting up the application")
    application = create_application(options.debug)

    # warn about --force-json
    if options.force_json:
        log.warn("Application started with '--force-json' option.  All calls will be treated as if they passed the 'Content-Type: application/json' header.  This may cause unexpected behavior.")

    # server startup
    if options.unix_socket:
        unix_socket_server(application, options)
    elif options.certfile and options.keyfile:
        https_server(application, options)
    else:
        http_server(application, options)

    # start the ioloop
    log.info("Starting the IOLoop")
    IOLoop.instance().start()
