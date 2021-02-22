# pySolPro
A automated self-generating command-line tool for Solace appliances.
This tool scans the imported solace_semp_api and renders the Api into a command-line tool with some basic ability to 
create, update and delete Solace managed objects.

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

## Status

Most commands work with some limitations. 

1. Delete does NOT work, because python sends a "empty" body to Solace, which expects NO body whatsover. 
2. --where only supports ONE where parameter, due to solace not accepting %2C encoded ","

## Setup

Create a virtual environment for this

    python3 -m venv ~/spvenv
    source ~/spvenv/bin/activate

Generate the python-config API for the version of the appliance you need using https://github.com/unixunion/solace_semp_client

    git clone https://github.com/unixunion/solace_semp_client.git
    cd solace_semp_client
    ./build.sh python 9.8.0.12
    # for each dir of python_config, python_monitor, python_action
    cd output/${dir}
    # be sure you activated the venv above! 
    python setup.py install

Install PyYAML

    pip install pyyaml

## Running

Simply provide what the method's help requires, parameters are passed directly on command line, and some, like body, are 
labeled in the help as being file: Class. These must have the body argument provide a path to a YAML file.

    python pysolpro.py config create_dmr_cluster --help
    python pysolpro.py config create_dmr_cluster --body data/dmr/dmr-cluster.yaml

#### Special parameters

##### override

When creating/updating existing objects on the appliance, you can override any attributes read from the yaml files with 
the `--override key val` parameter. For example if you want to change the enabled state(s) of a MessageVPN.

    ./pysolpro.py config update_msg_vpn \
        --msg_vpn_name default \
        --body default-vpn.yaml \
        --override enabled false \
        --override dmrEnabled false

##### where

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


### Changing the state of something

Changes are sent to the appliance using the Yaml files, but with some additional arguments to identify the object to 
update. For instance when creating an object initially, it is often enough to ship send the yaml body only, but when 
updating, you need to name the object you are updating. Overrides can also be used to alter some yaml attributes before
sending them to the appliance. 

    python pysolpro.py config update_dmr_cluster \
        --dmr_cluster_name mydmr \
        --body data/dmr/dmr-cluster.yaml \
        --override enabled false 

### Yaml Files

You can get the YAML representation of a object with almost any of the get_* subcommands, 
though some fields should be commented out for compatibility reasons. See the data/ examples

### Adding more manager types

Currenctly "action", "config" and "monitor" are all present. So there is no need for this. But if you want to know.

Add/Removing manager types is controlled via the "klasses" kwarg, that is passed into AutoApi upon instantiation.

TODO/FIXME make this source of truth the yaml config.

    klasses = [
        {
            "api": ConfigAllApi,
            "subcommand": "config",
            "config_class": solace_semp_config.Configuration,
            "client_class": solace_semp_config.ApiClient
        },
        {
            "api": MonitorAllApi,
            "subcommand": "monitor",
            "config_class": solace_semp_monitor.Configuration,
            "client_class": solace_semp_monitor.ApiClient
        },
        {
            "api": ActionAllApi,
            "subcommand": "action",
            "config_class": solace_semp_action.Configuration,
            "client_class": solace_semp_action.ApiClient
        }
    ]

### Optional Extras
#### Tab completion

pySolPro supports tab completion, and will create a cache file named pysolpro.cache upon first invocation. 
see https://kislyuk.github.io/argcomplete/ for more info

    pip install argcomplete

For zsh:
    
    # one time
    autoload -U bashcompinit
    bashcompinit
    # add this to end of ~/.zshrc
    # source the venv that you installed argcomplete into, should be same as PySolPro venv.
    source ~/spvenv/bin/activate
    eval "$(register-python-argcomplete pysolpro.py)"

#### Colourized logs

    pip install coloredlogs

### Notes 

#### Using the nw client

    ./server.py
    ./client.py config get_msg_vpn_queues --msg_vpn_name default |grep queueName | awk -F ": " '{print $2;}' | \
        xargs -I{} ./client.py config get_msg_vpn_queue_subscriptions --msg_vpn_name default --queue {}
