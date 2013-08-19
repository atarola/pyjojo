# pyJoJo

Expose a directory of bash scripts as an API.

## Tutorial

Create a directory to store the bash scripts, by default pyJoJo will be pointed at /srv/jojo.

Next, add a file to the directory as a test script.

In /srv/jojo/echo.sh:

    #!/bin/bash
    
    # -- jojo --
    # description: echo script
    # param: text - text to echo back
    # lock: false
    # -- jojo -- 
    
    echo $TEXT

Make sure this script is both readable and executable by the user pyJoJo is running under.  Scripts will be executed through the shell, so make sure you have a valid shebang line.

Now, start up pyJoJo and hit it with curl:

    pyjojo -d --dir /srv/jojo
    curl -k -XPOST http://localhost:3000/script/echo -d'{"text": "hello world!"}'

You should see this as a response:

    [TODO: add response]

## API

### JoJo Block Markup

JoJo blocks are metadata about the script that pyJoJo will use to execute it.  JoJo blocks are not mandatory for the script to run.

Example block:

    # -- jojo --
    # description: echo script
    # param: text - text to echo back
    # lock: false
    # -- jojo -- 

Fields:

  - **description**: information about what a script does
    - format: description: [*text*]
  - **param**: specifies a parameter to the script, will be passed in as environment params, with the name in all caps.
    - format: param: *name* [- *description*]
  - **lock**: if true, only one instance of the script will be allowed to run
    - format: lock: True|False
    
### Script List

Returns information about all the scripts.

    GET /scripts

### Get Information about a Script

Returns information about the specified script.

    GET /scripts/{script_name}

### Run a Script

Executes the specified script and returns the results.

    POST /scripts/{script_name}

### Reload the script directories

Reloads the scripts in the script directory.

    POST /reload

## Development Setup

### Setup Virtualenv
        
Install pip, virtualenv, and paver:

    sudo easy_install pip
    sudo pip install virtualenv paver

### Setup the Application

Clone the application:

    cd /path/to/workspace
    git clone [git path] [dir]
    cd [dir]
    paver create_virtualenv

To activate your virtualenv and run the service:
  
    cd /path/to/workspace/[dir]
    source bin/activate
    ebil -d

To deactivate the virtualenv:

    deactivate

