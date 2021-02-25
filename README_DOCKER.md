# pysolpro

python-solace-provision, or pysolpro for short, is a commandline tool which is generated from Solace SEMPv2 APIs. 
It provides CRUD operations for solace managed objects using YAML files as the underlying data layer.

For source, see https://github.com/unixunion/py-solace-provision

Different versions are provided to different appliance SEMP versions. The version of the container is the pysolpro version, 
followed by the SEMP API version for that version. e.g:

    0.0.2-9.8.0.12 -> pysolpro 0.0.2, for SEMP version 9.8.0.12

## Config File

The config file is rather straight forward. Here is an example for a local solace broker with all three
API's exposed.

    ---
    solace_config:
      config:
        host: http://172.17.0.1:8080/SEMP/v2/config
        username: admin
        password: admin
      monitor:
        host: http://172.17.0.1:8080/SEMP/v2/monitor
        username: admin
        password: admin
      action:
        host: http://172.17.0.1:8080/SEMP/v2/action
        username: admin
        password: admin
      #proxy: http://localhost:5555
    
    commands:
      config:
        module: solace_semp_config
        models: solace_semp_config.models
        api_class: MsgVpnApi
        config_class: Configuration
        client_class: ApiClient
      monitor:
        module: solace_semp_monitor
        models: solace_semp_monitor.models
        api_class: MsgVpnApi
        config_class: Configuration
        client_class: ApiClient
      action:
        module: solace_semp_action
        models: solace_semp_action.models
        api_class: MsgVpnApi
        config_class: Configuration
        client_class: ApiClient

    


## Running

The yaml config needs to be mounted at a specific location inside the container.

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        unixunion/pysolpro:0.0.2-9.8.0.12 config --help

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        unixunion/pysolpro:0.0.2-9.8.0.12 config create_msg_vpn --help

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        unixunion/pysolpro:0.0.2-9.8.0.12 \
        config get_msg_vpns


## Yaml Data Files

Every solace managed object can be provisioned and updated from YAML data. The yaml data should be mounted into the 
container. e.g:

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        -v `pwd`/data:/data  unixunion/pysolpro:0.0.2-9.8.0.12 \
        config create_msg_vpn --body /data/vpn.yaml

### Yaml Examples

In order to create YAML [data](https://github.com/unixunion/py-solace-provision/tree/master/data) files, simply query the appliance for the data. Note that some properties cannot be queried, 
such as credentials, and certificates.

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        -v `pwd`/data:/data  unixunion/pysolpro:0.0.2-9.8.0.12 \
        config get_msg_vpn --msg_vpn_name default

The output from the above can be saved to file, and used as body payload for CRUD operations. 

See https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/createMsgVpn for
more information about what fields should be present.

### Saving Yaml

An experimental option `--save` and `--save-dir` allow retrieved objects to write out to the savedir location. 

    docker run -v `pwd`/output:/savedata \
        -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        unixunion/pysolpro:0.0.2-9.8.0.12 \
            --save --save-dir /savedata \
                config get_msg_vpn --msg_vpn_name default 

## Tutorial

Download the [source](https://github.com/unixunion/py-solace-provision) code to get the [data](https://github.com/unixunion/py-solace-provision/tree/master/data) examples.

    git clone https://github.com/unixunion/py-solace-provision.git

Bring up a local broker or two

    docker-compose up -d

Get the IP address of your desktop from the perspective of the container

    docker run -ti busybox:latest /bin/ip route|awk '/default/ { print $3 }'
    172.17.0.1

Create a config file using above

    ---
    solace_config:
      config:
        host: http://172.17.0.1/SEMP/v2/config
        username: admin
        password: admin
    commands:
      config:
        module: solace_semp_config
        models: solace_semp_config.models
        api_class: MsgVpnApi
        config_class: Configuration
        client_class: ApiClient

Run PySolPro

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        unixunion/pysolpro:0.0.2-9.8.0.12 \
        config get_msg_vpn \
            --msg_vpn_name default

Lets provision a Queue using a YAML file

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        -v `pwd`/data:/data  unixunion/pysolpro:0.0.2-9.8.0.12 \
        config create_msg_vpn_queue \
            --msg_vpn_name default --body /data/queue.yaml

Lets change the queue enabled state

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        -v `pwd`/data:/data unixunion/pysolpro:0.0.2-9.8.0.12 \
        config update_msg_vpn_queue \
            --msg_vpn_name default \
            --queue_name test \
            --body /data/queue.yaml \
            --override egressEnabled false


### Common Pitfals

#### Incompatible properties

If downloading yaml from an appliance, some keys need to be removed due to incompatibility. Anything with a null value 
can be removed. The --save option will do this automatically e.g:

    eventServiceWebConnectionCountThreshold:
      clearPercent: 60
      clearValue: null
      setPercent: 80
      setValue: null

Solace has incompatible keys in some objects, like above. You cannot have clearPercentage and clearValue set at same time. 
And you will get an error:

    "error":{
        "code":11,
        "description":"Conflicting attribute \"clearValue\" used with \"clearPercent\".",
        "status":"INVALID_PARAMETER"
    },


If you are using the incorrect version of pySolPro to talk to a older appliance, you will get errors about unsupported properties.

    "error":{
        "code":11,
        "description":"Unknown attribute 'redeliveryEnabled'",
        "status":"INVALID_PARAMETER"
    },

#### Missing AllApi Config

Older versions of the broker do not have the AllApi, in these cases you will get an error like

    AttributeError: module 'solace_semp_config' has no attribute 'AllApi'

Simply change AllApi to MsgVpnApi in the commands config section.

    commands:
      config:
        ..
        api_class: MsgVpnApi
        ..
      monitor:
        ..
        api_class: MsgVpnApi
        ..
      action:
        ..
        api_class: MsgVpnApi
        ..


#### Missing Action and Monitor API

Versions of SEMPv2 before 9.1.0.77 did not ship with the specification for these commands. Simply remove them from the
yaml configuration.