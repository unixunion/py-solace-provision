# pySolPro
A automated self-generating command-line tool for Solace appliances.
This tool scans the imported solace_semp_api and renders the Api into a command-line tool with some basic ability to 
create, update and delete Solace managed objects.

Example:

    pysolpro.py [config|monitor|action] --help

    pysolpro.py config create_msg_vpn --body data/vpn.yaml

    pysolpro.py config update_msg_vpn \
        --msg_vpn_name myvpn \
        --body data/vpn.yaml \
        --override enabled false

    pysolpro.py config update_msg_vpn \
        --msg_vpn_name myvpn \
        --body data/vpn.yaml \
        --override dmrEnabled false \
        --override enavled false

## Setup

Create the a virtualenvironment for this

    python3 -m venv ~/spvenv
    source ~/spvenv/bin/activate

Generate the python-config API for the version of the appliance you need using https://github.com/unixunion/solace_semp_client

    git clone https://github.com/unixunion/solace_semp_client.git
    cd solace_semp_client
    ./build.sh python 9.8.0.12
    cd output/python_config
    # be sure you activated the venv above! 
    python setup.py install

Install PyYAML

    pip install pyyaml

## Running

    python pysolpro.py --help
    
### Manageing objects

Simply provide what the method's help requires, parameters are passed directly on command line, and some, like body, are 
labeled in the help as being file: Class. These must have the body argument provide a path to a YAML file.

    python pysolpro.py config create_dmr_cluster --help
    python pysolpro.py config create_dmr_cluster --body data/dmr/dmr-cluster.yaml

### Changing the state of something

You can override any key in the yaml with the --override arg.
Case sensitive.

    python pysolpro.py config update_dmr_cluster \
        --dmr_cluster_name mydmr \
        --body data/dmr/dmr-cluster.yaml \
        --override enabled false 

### Yaml Files

You can get the YAML representation of a object with almost any of the get_* subcommands, 
though some fields should be commented out for compatibility reasons. See the data/ examples

### Adding more managed types

Add the appropriate model, and API into the "klasses" field of the AutoManageGenerator class.

    klasses = [
        {"api": ConfigAllApi, "command": "config"},
        {"api": MonitorAllApi, "command": "monitor"},
        {"api": ActionAllApi, "command": "action"}
    ]

### Optional Extras
#### Tab completion

pySolPro supports tab completion, and will create a cache file named pysolpro.cache upon first invocation. 
see https://kislyuk.github.io/argcomplete/ for more info

    pip install argcomplete

For zsh:

    eval "$(register-python-argcomplete pysolpro.py)"

#### Colourized logs

    pip install coloredlogs

### Notes 

#### Using the nw client

    ./server.py
    ./client.py config get_msg_vpn_queues --msg_vpn_name default |grep queueName | awk -F ": " '{print $2;}' | \
        xargs -I{} ./client.py config get_msg_vpn_queue_subscriptions --msg_vpn_name default --queue {}