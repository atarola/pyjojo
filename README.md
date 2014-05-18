# pyJoJo

Expose a directory of bash scripts as an API.

# Recent Breaking Changes!

Pyjojo now supports the use of alternative HTTP methods (defined in your script).  To support this, we changed the previous GET calls to OPTIONS calls.

Output is now split on newlines and is an Array.

Output can now be combined via the 'output' jojo block argument.  Default is 'split'.

# Other Recent Changes

You now have the ability to generate named return values.  Pyjojo will look for lines that contain 'jojo_return_value key=value'.  These will show up in the output in a dictionary.

*Note*: return values MUST show up in stdout

Added the ability to start pyjojo with --force-json.  Should only be used if you absolutely must; i.e. you're using a 3rd party application that will not set the "Content-Type: application/json" header properly.

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
    echo "jojo_return_value name=bob"
    echo "jojo_return_value age=99"
    exit 0

Make sure this script is both readable and executable by the user pyJoJo is running under.  Scripts will be executed through the shell, so make sure you have a valid shebang line.

Now, start up pyJoJo and hit it with curl:

    pyjojo -d --dir /srv/pyjojo
    curl -XPOST http://localhost:3000/scripts/echo -H "Content-Type: application/json" -d '{"text": "hello world!"}'

You should see this as a response:

    {
      "retcode": 0,
      "return_values": {
          "age": "99", 
          "name": "bob"
      },
      "stderr": [],
      "stdout": [
          "echo'd text: hello world!"
      ]
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
      --force-json          Treats all calls as if they sent the 'Content-Type: application/json' header.  May produce unexpected results
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
    # http_method: get
    # lock: False
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
  - **http_method**: specifies the http method the script should respond to.
    - format: http_method: get
    - allowed_values: get|put|post|delete
    - default: post
  - **output**: specifies if the output should be 'split' into stderr and stdout or 'combined' into stdout.
    - format: output: combined
    - allowed_values: split|combined
    - default: split
  - **lock**: if true, only one instance of the script will be allowed to run
    - format: lock: True
    - default: False
    
### Script List

Returns information about all the scripts.

    OPTIONS /scripts

### Get Information about a Script

Returns information about the specified script.

    OPTIONS /scripts/{script_name}

### Run a Script

Executes the specified script and returns the results.

    POST /scripts/{script_name}

### Reload the script directories

Reloads the scripts in the script directory.

    POST /reload
