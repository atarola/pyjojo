## pyJoJo

Expose a directory of bash scripts as an API.

### Tutorial

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

Make sure this script is both readable and executable by the user pyJoJo is running under.  It will be executed as a bash script, so if you'd like to execute scripts in other languages, make sure you have a valid shebang line in it.

Now, start up pyJoJo and hit it with curl:

    pyjojo -d --dir /srv/jojo
    curl -k -XPOST http://localhost:3000/script/echo -d'{"text": "hello world!"}'

You should see this as a response:

    [TODO: add response]

### API

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
    
#### Script List

Returns information about all the scripts.

    GET /scripts

#### Get Information about a Script

Returns information about the specified script.

    GET /scripts/{script_name}

#### Run a Script

Executes the specified script and returns the results.

    POST /scripts/{script_name}

#### Reload the script directories

Reloads the scripts in the script directory.

    POST /reload

### Developer Setup

