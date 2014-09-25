#!/usr/bin/env python

import logging
import os
import os.path
import pipes
import re
import subprocess

from tornado import gen
from tornado.process import Subprocess
from tornado.ioloop import IOLoop
import toro

log = logging.getLogger(__name__)


class ScriptCollection(dict):
    """ load the collection of scripts """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        
    def metadata(self, tags):
        """ return the metadata for all of the scripts, keyed by name """
        
        output = {}
        
        for key, value in self.items():

            if (tags['tags']) or (tags['not_tags']) or (tags['any_tags']):
                if (set(tags['tags']).issubset(value.tags)) and (tags['tags']):
                    output[key] = value.metadata()
                    continue
                if tags['not_tags']:
                    output[key] = value.metadata()
                    for tag in tags['not_tags']:
                        if (tag in value.tags):
                            output.pop(key,None)
                            break
                for tag in tags['any_tags']:
                    if tag in value.tags:
                        output[key] = value.metadata()
                        break
            else:
                output[key] = value.metadata()
        
        return output

    def name(self, tags):
        """ return a list of just the names of all scripts """

        output = []

        for key, value in self.items():
            if (tags['tags']) or (tags['not_tags']) or (tags['any_tags']):
                if (set(tags['tags']).issubset(value.tags)) and (tags['tags']):
                    output.append(value.name)
                    continue
                if tags['not_tags']:
                    output.append(value.name)
                    for tag in tags['not_tags']:
                        if (tag in value.tags):
                            output.remove(value.name)
                            break
                for tag in tags['any_tags']:
                    if tag in value.tags:
                        output.append(value.name)
                        break
            else:
                output.append(value.name)

        return output


class Script(object):
    """ a single script in the directory """
    
    def __init__(self, filename, name, description, params, filtered_params, tags, http_method, output, needs_lock):
        self.lock = toro.Lock()
        self.filename = filename
        self.name = name
        self.description = description
        self.params = params
        self.filtered_params = filtered_params
        self.tags = tags
        self.http_method = http_method
        self.needs_lock = needs_lock
        self.output = output

    def filter_params(self, params):
        filtered_params = dict(params)
        for k,v in filtered_params.items():
            if k in self.filtered_params:
                filtered_params[k] = 'FILTERED'
        return filtered_params

    @gen.engine
    def execute(self, params, callback):
        log.info("Executing script: {0} with params: {1}".format(self.filename, self.filter_params(params)))
        
        if self.needs_lock:
            with (yield gen.Task(self.lock.aquire)):
                response = yield gen.Task(self.do_execute, params)
        else:
            response = yield gen.Task(self.do_execute, params)

        callback(response)

    @gen.engine
    def do_execute(self, params, callback):
        env = self.create_env(params)
        
        if self.output == 'combined':
            child = Subprocess(
                    self.filename,
                    env=env,
                    stdout=Subprocess.STREAM,
                    stderr=subprocess.STDOUT,
                    io_loop=IOLoop.instance()
                )
        
            retcode, stdout = yield [
                gen.Task(child.set_exit_callback),
                gen.Task(child.stdout.read_until_close)
            ]
            
            callback((child.returncode, stdout.split()))
        else:
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
            
            callback((child.returncode, stdout.splitlines(), stderr.splitlines()))

    def create_env(self, input):
        output = {}
        
        # add all the parameters as env variables
        for param in self.params:
            name = param['name']
            value = input.get(name, '')
            output[name.upper()] = pipes.quote(pipes.quote(value))
        
        return output

    def metadata(self):
        return {
            "filename": self.filename,
            "http_method": self.http_method,
            "name": self.name,
            "description": self.description,
            "params": self.params,
            "filtered_params": self.filtered_params,
            "tags": self.tags,
            "output": self.output,
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
    filtered_params = []
    tags = []
    http_method = 'post'
    output = 'split'
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
        
        # http_method
        if in_block and key == "http_method":
            if value.lower() in ['get','post','put','delete']:
                http_method = value.lower()
                continue
            else:
                log.warn("unrecognized http_method type in jojo block: {0}".format(value.lower()))
                continue
        
        # output
        if in_block and key == "output":
            if value.lower() in ['split','combined']:
                output = value.lower()
                continue
            else:
                log.warn("unrecognized output type in jojo block: {0}".format(value.lower()))
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

        # filtered_params
        if in_block and key == "filtered_params":
            filter_values = [filter_value.strip() for filter_value in value.split(',')]
            if len(filter_values) > 1:
                for filter_value in filter_values:
                    filtered_params.append(filter_value)
                continue

            filtered_params.append(value)
            continue

        # tags
        if in_block and key == "tags":
            tag_values = [tag_value.strip() for tag_value in value.split(',')]
            if len(tag_values) > 1:
                for tag_value in tag_values:
                    tags.append(tag_value)
                continue

            tags.append(value)
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
    
    return Script(filename, script_name, description, params, filtered_params, tags, http_method, output, lock)
