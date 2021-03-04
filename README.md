# py-solace-provision

An automated self-generating command-line tool for Solace appliances. This tool scans the imported `solace_semp_api` and 
renders the Api into a command-line tool with some basic ability to create, update and delete Solace managed objects.

Example:

    pysolpro.py [config|monitor|action] --help  

    pysolpro.py config create_msg_vpn --body data/vpn.yaml

    pysolpro.py action do_msg_vpn_clear_stats --msg_vpn_name default --body data/empty.yaml

    pysolpro.py config update_msg_vpn \
        --msg_vpn_name myvpn \
        --body data/vpn.yaml \
        --override dmrEnabled false \
        --override enabled false

    pysolpro.py action get_msg_vpns --where enabled==false

    pysolpro.py config get_msg_vpn_queues --msg_vpn_name default 2>&1 | grep queueName

## Status

Most commands work with some limitations. 

1. `--where` only supports ONE where parameter, due to solace OpenAPI spec being v2, and the API not accepting %2C encoded 
   comma. If Solace moves to OpenAPIv3, there is a `allowReserved` setting to prevent encoding of reserved characters.
2. Argparse sometimes reports the incorrect missing required positional argument, see --help for the command when this 
   occurs.

    ./pysolpro.py config update_dmr_cluster --body data/dmr/dmr-cluster.yaml                   
    ERROR type error update_dmr_cluster() missing 1 required positional argument: 'body'

## Docker

Docker images available at https://hub.docker.com/r/unixunion/pysolpro

## Installation

Create a virtual environment for this

    python3 -m venv ~/spvenv
    source ~/spvenv/bin/activate

Install dependencies, where SOLACE_VERSION equals your broker version or closest match. 
see [https://pypi.org/project/solace-semp-config/](https://pypi.org/project/solace-semp-config/) for available versions 

    # required
    pip install -r requirements.txt
    pip install solace-semp-config==SOLACE_VERSION
    
optional action and monitor api support

    pip install solace-semp-action==SOLACE_VERSION
    pip install solace-semp-monitor==SOLACE_VERSION

Optional extras

    pip install argcomplete
    pip install coloredlogs

Now you can run `python pysolpro.py` --help

## Broker Configuring

See solace.yaml for how to set up broker credentials and API endpoints.

    PYSOLPRO_CONFIG=data/broker1.yaml

If the config file above is not found, it is searched for in the following locations:

    ".",
    "/",
    "/opt/pysolpro",
    "/etc/pysolpro"

The config file also denotes which API's to generate commands for. There are 3 API's available, `config`, `action` and `monitor`.
These depend on the `pip` installed `solace-semp-*` packages from Installation steps.

Configuring the API's example:

    commands:
      config:
        module: solace_semp_config
        api_class: AllApi
        config_class: Configuration
        client_class: ApiClient
      monitor:
        module: solace_semp_monitor
        api_class: AllApi
        config_class: Configuration
        client_class: ApiClient
      action:
        module: solace_semp_action
        api_class: AllApi
        config_class: Configuration
        client_class: ApiClient

Older versions of SEMPv2 api do not have the `AllApi` interface, in those cases use `MsgVpnApi` instead.

Solace broker configs are needed for each `API` you want to invoke.

    solace_config:
      config:
        host: http://localhost:8080/SEMP/v2/config
        username: admin
        password: admin
      monitor:
        host: http://localhost:8080/SEMP/v2/monitor
        username: admin
        password: admin
      action:
        host: http://localhost:8080/SEMP/v2/action
        username: admin
        password: admin


## Object Files

All solace managed objects can be represented as YAML files. see [data/](data/) for some examples. These can be created 
by querying the appliance for the relevant object. Note that some attributes are NOT retrieved from appliances during 
GET operations. Some examples are items such as credentials.

Solace has a tendency to have incompatible attributes, and these should be removed from YAML before submitting to appliance. 
Examples of these are commented out in [data/](/data) files. For example, you cannot use clearPercent and clearValue at 
same time.

    eventEgressFlowCountThreshold:
      clearPercent: 40
    #  clearValue: 0
      setPercent: 60
    #  setValue: 0

When using `--save`, these incompatible attributes are null valued, and are removed when writing to disk.

You also cannot mix authentication mechanisms, like password and certificate. Choose one. 

    replicationBridgeAuthenticationBasicClientUsername: ""
    replicationBridgeAuthenticationBasicPassword: ""
    # replicationBridgeAuthenticationClientCertContent: ""
    # replicationBridgeAuthenticationClientCertPassword: ""

The response from the appliance will generally indicate if you have incompatible configurations.

        "error":{
            "code":89,
            "description":"Problem with replicationBridgeAuthenticationClientCertContent or replicationBridgeAuthenticationClientCertPassword: Channel not encrypted",
            "status":"NOT_ALLOWED"
        },

When using Object Files to create/update managed objects on the broker, you can use the `--override` argument to override 
any attribute in the YAML files. As an example, this can be used enable/disable services. It can also be used to 
"template" objects. e.g:

    pysolpro.py config create_msg_vpn --body data/vpn.yaml --override msgVpnName myVpn
    pysolpro.py config create_msg_vpn --body data/vpn.yaml --override msgVpnName anotherVpnSameYaml

## Running

Simply provide what the method's help requires, parameters are passed directly on command line, and some, like body, are 
labeled in the help as being `file: ClassName`. These must have their argument provide a path to a YAML file.

    python pysolpro.py config create_dmr_cluster --help
    usage: pySolPro config create_msg_vpn [-h] [--body BODY] [--override OVERRIDE OVERRIDE]
    
    optional arguments:
      -h, --help            show this help message and exit
      --body BODY           file: MsgVpn
      --override OVERRIDE OVERRIDE
                            key,val in yaml to override, such as enabled false

    python pysolpro.py config create_dmr_cluster --body data/dmr/dmr-cluster.yaml


#### Special parameters

##### --override

When creating/updating objects on the appliance, you can override any attributes read from the yaml files with the 
`--override KEY VALUE` argument. For example if you want to change the enabled state(s) of a MessageVPN.

    ./pysolpro.py config update_msg_vpn \
        --msg_vpn_name default \
        --body default-vpn.yaml \
        --override enabled false \
        --override dmrEnabled false

Multiple `--override` argyments can be provided.

##### --where

Include in the response only objects where certain conditions are true. Use this query parameter to limit which objects 
are returned to those whose attribute values meet the given conditions.

The value of where is a comma-separated list of expressions. All expressions must be true for the object to be included 
in the response. Each expression takes the form:

expression  = attribute-name OP value
OP          = '==' | '!=' | '&lt;' | '&gt;' | '&lt;=' | '&gt;='

value may be a number, string, true, or false, as appropriate for the type of attribute-name. Greater-than and less-than 
comparisons only work for numbers. A * in a string value is interpreted as a wildcard (zero or more characters).

Note, only one where condition is supported at the moment, due to Solace not using OpenAPI3. OpenAPI2 does not have `allowReserved`
keyword in the parameter specification, so the `,` separator is encoded to %2C.

Example:

    ./pysolpro.py config get_msg_vpn_queues --msg_vpn_name default --where "queueName==B*"
    ./pysolpro.py config get_msg_vpn_queues --msg_vpn_name default --where "enabled==false"
    ./pysolpro.py monitor get_msg_vpn_queues --msg_vpn_name default --where "spooledByteCount>1000000"


#### Changing the state of something

Changes are sent to the appliance using the Yaml files, but with some additional arguments to identify the object to 
update. For instance when creating an object initially, it is often enough to ship send the yaml body only, but when 
updating, you need to name the object you are updating. Overrides can also be used to alter some yaml attributes before
sending them to the appliance. 

    python pysolpro.py config update_dmr_cluster \
        --dmr_cluster_name mydmr \
        --body data/dmr/dmr-cluster.yaml \
        --override enabled false 

### Yaml Files

You can get the YAML representation of an object with almost any of the get_* subcommands, 
though some fields should be commented out for compatibility reasons. See the data/ examples.

#### Saving Yaml

The `--save` option writes out to the retrieved object(s) to the `--save-dir` location.

    python pysolpro.py --save --save-dir savedata config get_msg_vpn --msg_vpn_name default 

You can also save multiple objects when using the "plural" getters.

    python pysolpro.py --save --save-dir savedata config get_msg_vpns

#### Saved File Naming / Mappings

Due to the varying content types of objects, `data_mappings` from the configuration file are used to determine which 
key in the data to use for the filename, or alternatively hash the payload for smalled config increments.

### Optional Extras
#### Tab completion

pySolPro supports tab completion, and will create a cache file named pysolpro.cache upon first invocation. 
see [argcomplete](https://kislyuk.github.io/argcomplete/) for more info

    pip install argcomplete

For zsh:
    
    # one time
    autoload -U bashcompinit
    bashcompinit
    # add this to end of ~/.zshrc
    # source the venv that you installed argcomplete into, should be same as PySolPro venv.
    source ~/spvenv/bin/activate
    eval "$(register-python-argcomplete pysolpro.py)"

To populate the cache, run the --help command:

    ./pysolpro.py --help

#### Colourized logs

    pip install coloredlogs

### Notes 

#### Using the nw client

    ./server.py
    ./client.py config get_msg_vpn_queues --msg_vpn_name default |grep queueName | awk -F ": " '{print $2;}' | \
        xargs -I{} ./client.py config get_msg_vpn_queue_subscriptions --msg_vpn_name default --queue {}

#### Building docker image

Pass the version of SEMP to build for as a buld-arg. See [docker_deps/semp_config](docker_deps/semp_config) for bundled versions.
You can add your own just by dropping in the appropriate yaml specs.

    docker build --build-arg sempver=9.8.0.12 -t unixunion/pysolpro:dev . 

##### Building all versions

    ls docker_deps/semp_config | xargs -I {} -t docker build --build-arg sempver={} -t unixunion/pysolpro:0.0.2-{} .

##### Testing all versions

    ls docker_deps/semp_config | xargs -I {} -t docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml unixunion/pysolpro:0.0.2-{} config get_msg_vpn --msg_vpn_name default

##### Getting all SEMPv2 client whl files

    ls docker_deps/semp_config | xargs -I@ -t docker create unixunion/pysolpro:0.1.1-@ | xargs -I@ docker cp @:/tmp output

##### Releasing wheel to pypi

###### solace_semp_* wheels
    
    ls docker_deps/semp_config | xargs -I@ -t docker build --build-arg sempver=@ -t unixunion/pysolpro:0.1.3-@ . -f docker_deps/Dockerfile
