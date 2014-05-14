#!/usr/bin/env python

import logging
import sys

from tornado.httpserver import HTTPServer
from tornado.netutil import bind_unix_socket

log = logging.getLogger(__name__)

def https_server(application, options):
    """ https server """

    log.info("Binding application to unix socket {0}".format(options.unix_socket))
    if sys.version_info < (2,7,0):
        server = HTTPServer(application, ssl_options={
            "certfile": options.certfile,
            "keyfile": options.keyfile
        })
    else:
        server = HTTPServer(application, ssl_options={
            "certfile": options.certfile,
            "keyfile": options.keyfile,
            "ciphers": "HIGH,MEDIUM"
        })
    server.bind(options.port, options.address)
    server.start()

def http_server(application, options):
    """ http server """

    log.warn("Application is running in HTTP mode, this is insecure.  Pass in the --certfile and --keyfile to use SSL.")
    server = HTTPServer(application)
    server.bind(options.port, options.address)
    server.start()

def unix_socket_server(application, options):
    """ unix socket server """

    log.info("Binding application to unix socket {0}".format(options.unix_socket))
    server = HTTPServer(application)
    socket = bind_unix_socket(options.unix_socket)
    server.add_socket(socket)
