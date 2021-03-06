# py-solace-provision

An automated self-generating command-line tool for Solace appliances. This tool scans the imported `solace_semp_api` and 
renders the Api into a command-line tool with some basic ability to create, update and delete Solace managed objects.

Example:

```bash
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
```

## Status

Most commands work with some limitations. 

1. `--where` only supports ONE where parameter, due to solace OpenAPI spec being v2, and the API not accepting %2C encoded 
   comma. If Solace moves to OpenAPIv3, there is a `allowReserved` setting to prevent encoding of reserved characters.
2. Argparse sometimes reports the incorrect missing required positional argument, see --help for the command when this 
   occurs.

    ./pysolpro.py config update_dmr_cluster --body data/dmr/dmr-cluster.yaml                   
    ERROR type error update_dmr_cluster() missing 1 required positional argument: 'body'

## Dependencies

pySolPro imports one or several libraries available at runtime, [solace-semp-config](https://pypi.org/project/solace-semp-config/#description) library is required. The monitoring and action libraries are optional, and have a performance cost. So dont install monitor or action if you dont intend to use them. 

## Docker

Docker images are available at https://hub.docker.com/r/unixunion/pysolpro

## Installation

pySolPro depends on getting the closest version of the [solace-semp-config](https://pypi.org/project/solace-semp-config/#description) library. Use the closest version equal or less than your broker version from the versions available. 

### pip

Using pip, you can install pySolPro into your python environment.

```sh
pip install py-solace-provision
pip install solace-semp-config==SOLACE_VERSION
# optional
pip install solace-semp-monitor==SOLACE_VERSION
pip install solace-semp-action==SOLACE_VERSION
```

### manual

Create a virtual environment for this

```bash
python3 -m venv ~/spvenv
source ~/spvenv/bin/activate
```

Install dependencies, where SOLACE_VERSION equals your broker version or closest match. 
see [https://pypi.org/project/solace-semp-config/](https://pypi.org/project/solace-semp-config/) for available versions 

```bash
# required
pip install -r requirements.txt
pip install solace-semp-config==SOLACE_VERSION
```

optional action and monitor api support

```bash
pip install solace-semp-action==SOLACE_VERSION
pip install solace-semp-monitor==SOLACE_VERSION
```

Optional extras

```sh
pip install argcomplete
pip install coloredlogs
```

Now you can run `pysolpro.py --help`

## Configuring API

See [solace.yaml](solace.yaml) for how to set up broker credentials and API endpoint(s). pySolPro searches for a file named `solace.yaml` in several locations listed below, or you can pass the a config filename via an environment property, e.g:

```bash
PYSOLPRO_CONFIG=/full/path/to/config.yaml pysolpro.py config get_msg_vpns
```

You can also pass a partial path via the environment variable, which will then search the below mentioned locations for that file.

```bash
PYSOLPRO_CONFIG=relevant/path/to/config.yaml pysolpro.py config get_msg_vpns
```

If the above relevant config file is not immediately found in the current working directory, it is searched for in the following locations:

    ".",
    "~/.pysolpro/",
    "/",
    "/opt/pysolpro",
    "/etc/pysolpro"

The config file also denotes which API's pySolPro generates commands for. There are 3 API's available, `config`, `action` and `monitor`. `config` is required, and requires the `solace-semp-config` module. Both `action` and `monitor` are optional, and should not be installed if not using them, as it slows down the command parser.  

Configuring the API's example:

    commands:
      config:
        api_path: /SEMP/v2/config
        module: solace_semp_config
        models: solace_semp_config.models
        api_class: AllApi
        config_class: Configuration
        client_class: ApiClient
      monitor:
        api_path: /SEMP/v2/monitor
        module: solace_semp_monitor
        models: solace_semp_monitor.models
        api_class: AllApi
        config_class: Configuration
        client_class: ApiClient
      action:
        api_path: /SEMP/v2/action
        module: solace_semp_action
        models: solace_semp_action.models
        api_class: AllApi
        config_class: Configuration
        client_class: ApiClient

Older versions of SEMPv2 api do not have the `AllApi` interface, in those cases use `MsgVpnApi` instead.

Solace broker configs are needed for each `API` you want to invoke.

    solace_config:
      ssl:
        verify_ssl: false
        cert: certs/cert.pem
      config:
        host: http://localhost:8080
        username: admin
        password: admin
      monitor:
        host: http://localhost:8080
        username: admin
        password: admin
      action:
        host: http://localhost:8080
        username: admin
        password: admin


## Yaml Object Files

All solace managed objects can be represented as YAML files. see [data/](data/) for some examples. These can be created 
by querying the appliance for the relevant object. Note that some attributes are NOT retrieved from appliances during 
GET operations. Some examples are items such as credentials. There is a task to create this feature using the `opaque_password` parameter.

Solace Objects have a tendency to have incompatible attributes, and these should be removed from YAML before submitting to appliance. Examples of these are commented out in [data/](/data) files. For example, you cannot use clearPercent and clearValue at same time.

    eventEgressFlowCountThreshold:
      clearPercent: 40
    #  clearValue: 0
      setPercent: 60
    #  setValue: 0

When using `--save`, these most of these incompatible attributes are null valued, and are removed when writing the yaml to disk.

Other examples of incomatible types are authentication mechanisms, like password and certificate cannot both be used at the same time.

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

When using Object Files to create/update managed objects on the broker, you can use the `--override` argument to override any attribute in the YAML files before it is posted to the appliance. As an example, this can be used enable/disable services. It can also be used to "template" objects using the same yaml. e.g:

```bash
pysolpro.py config create_msg_vpn --body data/vpn.yaml --override msgVpnName myVpn
pysolpro.py config create_msg_vpn --body data/vpn.yaml --override msgVpnName anotherVpnSameYaml
```

## Running pySolPro

Simply provide what the method's help requires, parameters are passed directly on command line, and some, like body, are labeled in the help as being `file: <ClassName>`. These must have their argument provide a path to a YAML file.

    usage: pySolPro [-h] [--save] [--save-dir SAVEDIR] [--host HOST] [--username USERNAME] [--password PASSWORD] {config,monitor,action} ...
    
    positional arguments:
      {config,monitor,action}
                            sub-command help
    
    optional arguments:
      -h, --help            show this help message and exit
      --save                save retrieved data to disk
      --save-dir SAVEDIR    location to save to
      --host HOST           broker host override e.g: https://localhost:8843
      --username USERNAME   username override
      --password PASSWORD   password override
    
    PYSOLPRO_CONFIG=/path/to/broker_config.yaml python pysolpro.py config create_dmr_cluster --body data/dmr/dmr-cluster.yaml


#### Special parameters

##### --opaque_password

Allows you to upload/download secrets from the appliance. You must be using TLS.

##### --override

When creating/updating objects on the appliance, you can override any attributes read from the yaml files with the 
`--override KEY VALUE` argument. For example if you want to change the enabled state(s) of a MessageVPN.

    ./pysolpro.py config update_msg_vpn \
        --msg_vpn_name default \
        --body default-vpn.yaml \
        --override enabled false \
        --override dmrEnabled false

Multiple `--override` arguments can be provided.

##### --where

When querying the appliance with get_* commands, the SEMP API can filter the response to only include objects where certain conditions evaluate to true.

The value of where is a comma-separated list of expressions. All expressions must be true for the object to be included 
in the response. Each expression takes the form:

expression  = attribute-name OP value
OP          = '==' | '!=' | '&lt;' | '&gt;' | '&lt;=' | '&gt;='

value may be a number, string, true, or false, as appropriate for the type of attribute-name. Greater-than and less-than 
comparisons only work for numbers. A * in a string value is interpreted as a wildcard (zero or more characters).

Note, only one where condition is supported at the moment, due to Solace not using OpenAPI3. OpenAPI2 does not have `allowReserved` keyword in the parameter specification, so the `,` separator is encoded to %2C.

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

#### Building wheels

    pip install wheel
    python setup.py bdist_wheel --universal

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

##### Creating self signed cert

    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
    openssl rsa -in key.pem -out nopassskey.pem
    cat nopassskey.pem >>server.pem
    cat cert.pem >>server.pem

Jump into the broker and enable TLS

    docker exec -ti broker1 cli
    enable
    configure
    ssl
    server-certificate server.pem
    exit
    service semp
    shutown
    listen-port 8843 ssl
    no shutdown



