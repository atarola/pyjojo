#!/usr/bin/env python

import logging
import httplib
import json

from tornado import gen
from tornado.web import RequestHandler, HTTPError, asynchronous

from pyjojo.config import config
from pyjojo.scripts import create_collection
from pyjojo.util import route

log = logging.getLogger(__name__)


class BaseHandler(RequestHandler):
    """ Contains helper methods for all request handlers """    

    def prepare(self):
        self.params = {}
        content_type = self.request.headers.get("Content-Type", 'application/json')
    
        if content_type.startswith("application/json"):
            if self.request.body in [None, ""]:
                return

            self.params = json.loads(self.request.body)
        else:
            # we only handle

    def write(self, chunk):
        if isinstance(chunk, dict):
            chunk = json.dumps(chunk)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        
        super(BaseHandler, self).write(chunk)

    def write_error(self, status_code, **kwargs):
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
