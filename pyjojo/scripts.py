#!/usr/bin/env python

import logging
import os
import os.path
import re

from tornado import gen
from tornado.process import Subprocess
from tornado.ioloop import IOLoop
import toro

log = logging.getLogger(__name__)


class ScriptCollection(dict):
    """ load the collection of scripts """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        
    def metadata(self):
        """ return the metadata for all of the scripts, keyed by name """
        
        output = {}
        
        for key, value in self.items():
            output[key] = value.metadata()
        
        return output


class Script(object):
    """ a single script in the directory """
    
    def __init__(self, filename, name, description, params, needs_lock):
        self.lock = toro.Lock()
        self.filename = filename
        self.name = name
        self.description = description
        self.params = params
        self.needs_lock = needs_lock

    @gen.engine
    def execute(self, params, callback):
        log.info("Executing script: {0} with params: {1}".format(self.filename, params))
        
        if self.needs_lock:
            with (yield gen.Task(self.lock.aquire)):
                response = yield gen.Task(self.do_execute, params)
        else:
            response = yield gen.Task(self.do_execute, params)

        callback(response)

    @gen.engine
    def do_execute(self, params, callback):
        env = self.create_env(params)
                
        child = Subprocess(
                self.filename,
                env=env,
                stdout=Subprocess.STREAM,
                stderr=Subprocess.STREAM,
                io_loop=IOLoop.instance()
            )
    
        retcode, stdout, stderr = yield [
            gen.Task(child.set_exit_callback),
            gen.Task(child.stdout.read_until_close),
            gen.Task(child.stderr.read_until_close)
        ]
        
        callback((child.returncode, stdout, stderr))

    def create_env(self, input):
        output = {}
        
        # add all the parameters as env variables
        for param in self.params:
            name = param['name']
            output[name.upper()] = input.get(name, '')
        
        return output

    def metadata(self):
        return {
            "filename": self.filename,
            "name": self.name,
            "description": self.description,
            "params": self.params,
            "lock": self.needs_lock
        }
        
    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self.metadata())


def create_collection(directory):
    """ create the script collection for the directory """
    
    log.info("Getting scripts from directory {0}".format(directory))
    
    collection = ScriptCollection()
    
    for (dirpath, _, filenames) in os.walk(directory):                
        for filename in filenames:
            # grab the file's absolute path, and name
            path = os.path.join(dirpath, filename)
            full_path = os.path.abspath(path)

            # format the name for sanity
            name = path.replace(directory + os.sep, '')
            name = '.'.join(name.split(".")[:-1])
            name = re.sub(r'(\W)+', '_', name)
            
            log.info("Adding script with name: {0} and path: {1}".format(name, full_path))
            script = create_script(name, full_path)
            
            if script is not None:
                collection[name] = script

    return collection


def create_script(script_name, filename):
    """ parse a script, returning a Script object """
    
    # script defaults
    description = None
    params = []
    lock = False
    
    # warn the user if we can't execute this file
    if not os.access(filename, os.X_OK):
        log.error("file with filename {0} is not executable, Ignoring.".format(filename))
        return None
    
    # grab file contents
    with open(filename) as f:
        contents = list(f)
    
    in_block = False
    
    # loop over the contents of the file
    for line in contents:        
        
        # all lines should be bash style comments
        if not line.startswith("#"):
            continue
                
        # we don't need the first comment, or extranious whitespace
        line = line.replace("#", "").strip()
        
        # start of the jojo block
        if not in_block and line.startswith("-- jojo --"):
            in_block = True
            continue
        
        # end of the jojo block, so we'll stop here
        if in_block and line.startswith("-- jojo --"):
            in_block = False
            break
        
        # make sure the line is good
        if not ':' in line:
            continue
        
        # prep work for later
        key, value = [item.strip() for item in line.split(':')]
        
        # description
        if in_block and key == "description":
            description = value
            continue
        
        # param
        if in_block and key == "param":
            # handle the optional description
            if "-" in value:
                name, desc = [item.strip() for item in value.split('-')]
                params.append({'name': name, 'description': desc})
                continue
            
            params.append({'name': value})
            continue
        
        # lock
        if in_block and key == "lock":
            lock = (value == "True")
            continue
        
        log.warn("unrecognized line in jojo block: {0}".format(line))
    
    # if in_bock is true, then we never got an end to the block, which is bad
    if in_block:
        log.error("file with filename {0} is missing an end block, Ignoring".format(filename))
        return None
    
    return Script(filename, script_name, description, params, lock)
