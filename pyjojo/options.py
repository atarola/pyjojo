#!/usr/bin/env python

from optparse import OptionParser, IndentedHelpFormatter

from pyjojo.config import config

def command_line_options():
    """ command line configuration """
    
    parser = OptionParser(usage="usage: %prog [options] <htpasswd>")
    
    parser.formatter = PlainHelpFormatter()
    parser.description = """Expose a directory of bash scripts as an API.

Note: This application gives you plenty of bullets to shoot yourself in the 
foot!  Please use the SSL config options, give a password file, and either 
whitelist access to it via a firewall or keep it in a private network.

You can use the apache htpasswd utility to create your htpasswd files.  If
you do, I recommend passing the -d flag, forcing the encryption type pyjojo
recognises."""
    
    parser.add_option('-d', '--debug', action="store_true", dest="debug", default=False,
                      help="Start the application in debugging mode.")
    
    parser.add_option('--dir', action="store", dest="directory", default="/srv/pyjojo",
                      help="Base directory to parse the scripts out of")
    
    parser.add_option('-p', '--port', action="store", dest="port", default=3000,
                      help="Set the port to listen to on startup.")
    
    parser.add_option('-a', '--address', action ="store", dest="address", default=None,
                      help="Set the address to listen to on startup. Can be a hostname or an IPv4/v6 address.")
    
    parser.add_option('-c', '--certfile', action="store", dest="certfile", default=None,
                      help="SSL Certificate File")
    
    parser.add_option('-k', '--keyfile', action="store", dest="keyfile", default=None,
                      help="SSL Private Key File")
    
    parser.add_option('-u', '--unix-socket', action="store", dest="unix_socket", default=None,
                      help="Bind pyjojo to a unix domain socket")

    options, args = parser.parse_args()

    # TODO: only do this if they specify the ssl certfile and keyfile
    if len(args) >= 1:
        config['passfile'] = args[0]
    else:
        config['passfile'] = None
        
    config['directory'] = options.directory

    return options


class PlainHelpFormatter(IndentedHelpFormatter): 
    def format_description(self, description):
        if description:
            return description + "\n"
        else:
            return ""
