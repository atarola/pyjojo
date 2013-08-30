#!/usr/bin/env python

import logging
import httplib
import json
import crypt
import base64
import difflib

from tornado import gen
from tornado.web import RequestHandler, HTTPError, asynchronous

from pyjojo.config import config
from pyjojo.scripts import create_collection
from pyjojo.util import route

log = logging.getLogger(__name__)


class BaseHandler(RequestHandler):
    """ Contains helper methods for all request handlers """    

    def prepare(self):
        self.handle_params()
        self.handle_auth()

    def handle_params(self):
        """ automatically parse the json body of the request """
        
        self.params = {}
        content_type = self.request.headers.get("Content-Type", 'application/json')
            
        if content_type.startswith("application/json"):
            if self.request.body in [None, ""]:
                return

            self.params = json.loads(self.request.body)
        else:
            # we only handle json, and say so
            raise HTTPError(400, "This application only support json, please set the http header Content-Type to application/json")

    def handle_auth(self):
        """ authenticate the user """
        
        # no passwords set, so they're good to go
        if config['passwords'] == None:
            return
        
        # grab the auth header, returning a demand for the auth if needed
        auth_header = self.request.headers.get('Authorization')
        if (auth_header is None) or (not auth_header.startswith('Basic ')):
            self.auth_challenge()
            return
        
        # decode the username and password
        auth_decoded = base64.decodestring(auth_header[6:])
        username, password = auth_decoded.split(':', 2)
                
        # grab the crypted password, returning a challenge if the user doesn't exist
        crypted_password = config['passwords'].get(username, None)
        if crypted_password is None: 
            self.auth_challenge()
            return
        
        # crypt the passed in password with the salt as the hashed password
        pwhash = crypt.crypt(password, crypted_password)
        if crypted_password != pwhash:
            self.auth_challenge()
            return
    
    def auth_challenge(self):
        """ return the standard basic auth challenge """
        
        self.set_header("WWW-Authenticate", "Basic realm=pyjojo")
        self.set_status(401)
        self.finish()
            
    def write(self, chunk):
        """ if we get a dict, automatically change it to json and set the content-type """

        if isinstance(chunk, dict):
            chunk = json.dumps(chunk)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        
        super(BaseHandler, self).write(chunk)

    def write_error(self, status_code, **kwargs):
        """ return an exception as an error json dict """

        if kwargs['exc_info'] and hasattr(kwargs['exc_info'][1], 'log_message'):
            message = kwargs['exc_info'][1].log_message
        else:
            # TODO: What should go here?
            message = ''

        self.write({
            'error': {
                'code': status_code,
                'type': httplib.responses[status_code],
                'message': message
            }
        })


@route(r"/scripts/?")
class ScriptCollectionHandler(BaseHandler):
    
    def get(self):
        """ get the requirements for all of the scripts """
       
        self.finish({'scripts': self.settings['scripts'].metadata()})


@route(r"/scripts/([\w\-]+)/?")
class ScriptDetailsHandler(BaseHandler):
    
    def get(self, script_name):
        """ get the requirements for this script """
        
        script = self.get_script(script_name)
        self.finish({'script': script.metadata()})
    
    @asynchronous
    @gen.engine
    def post(self, script_name):
        """ run the script """
                
        script = self.get_script(script_name)
        retcode, stdout, stderr = yield gen.Task(script.execute, self.params)
        
        self.finish({
            "stdout": stdout,
            "stderr": stderr,
            "retcode": retcode
        })
        
    def get_script(self, script_name):
        script = self.settings['scripts'].get(script_name, None)
        
        if script is None:
            raise HTTPError(404, "Script with name '{0}' not found".format(script_name))

        return script


@route(r"/reload/?")
class ReloadHandler(BaseHandler):
    
    def post(self):
        """ reload the scripts from the script directory """
        self.settings['scripts'] = create_collection(config['directory'])
        self.finish({"status": "ok"})
