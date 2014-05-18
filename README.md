# pyJoJo

Expose a directory of bash scripts as an API.

## Tutorial

Create a directory to store the bash scripts, by default pyJoJo will be pointed at /srv/pyjojo.

Next, add a file to the directory as a test script.

In /srv/pyjojo/echo.sh:

    #!/bin/bash

    # -- jojo --
    # description: echo text on the command line
    # param: text - text to echo
    # -- jojo --

    echo "echo'd text: $TEXT"
    exit 0

Make sure this script is both readable and executable by the user pyJoJo is running under.  Scripts will be executed through the shell, so make sure you have a valid shebang line.

Now, start up pyJoJo and hit it with curl:

    pyjojo -d --dir /srv/pyjojo
    curl -XPOST http://localhost:3000/scripts/echo -H "Content-Type: application/json" -d '{"text": "hello world!"}'

You should see this as a response:

    {
      "retcode": 0, 
      "stderr": "", 
      "stdout": "echo'd text: hello world!\n"
    }

## Usage

    Usage: pyjojo [options] <htpasswd>

    Expose a directory of bash scripts as an API.

    Note: This application gives you plenty of bullets to shoot yourself in the
    foot!  Please use the SSL config options, give a password file, and either
    whitelist access to it via a firewall or keep it in a private network.

    You can use the apache htpasswd utility to create your htpasswd files.

    Options:
      -h, --help            show this help message and exit
      -d, --debug           Start the application in debugging mode.
      --dir=DIRECTORY       Base directory to parse the scripts out of
      -p PORT, --port=PORT  Set the port to listen to on startup.
      -a ADDRESS, --address=ADDRESS
                            Set the address to listen to on startup. Can be a
                            hostname or an IPv4/v6 address.
      -c CERTFILE, --certfile=CERTFILE
                            SSL Certificate File
      -k KEYFILE, --keyfile=KEYFILE
                            SSL Private Key File
      -u UNIX_SOCKET, --unix-socket=UNIX_SOCKET
                            Bind pyjojo to a unix domain socket

## API

### JoJo Block Markup

JoJo blocks are metadata about the script that pyJoJo will use to execute it.  JoJo blocks are not mandatory for the script to run.

Example block:

    # -- jojo --
    # description: echo script
    # param: text - text to echo back
    # param: secret1 - sensitive text you don't want logged
    # param: secret2 - more sensitive stuff
    # filtered_params: secret1, secret2
    # tags: test, staging
    # lock: false
    # -- jojo -- 

Fields:

  - **description**: information about what a script does
    - format: description: [*text*]
  - **param**: specifies a parameter to the script, will be passed in as environment params, with the name in all caps.  One per line.
    - format: param: *name* [- *description*]
  - **filtered_params**: specifies a list of parameters that you have already specified, but want to ensure that the values are not logged.
    - format: filtered_params: item1 [,item2]
  - **tags**: specifies a list of tags that you want displayed when querying pyjojo about scripts.
    - format: tags: item1 [,item2]
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
