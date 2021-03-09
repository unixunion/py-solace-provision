# pysolpro

python-solace-provision, or pysolpro for short, is a commandline tool which is generated from Solace SEMPv2 APIs. 
It provides CRUD operations for solace managed objects using YAML files as the underlying data layer.

For source, see https://github.com/unixunion/py-solace-provision

Different versions are provided to different appliance SEMP versions. The version of the container is the pysolpro version, 
followed by the SEMP API version for that version. e.g:

    0.2.8-9.8.0.12 -> pysolpro 0.2.8, for SEMP version 9.8.0.12

## Config File

The config file is rather straight forward. Here is an example for a local solace broker with all three
API's exposed.

    ---
    solace_config:
      ssl:
        verify_ssl: false
        cert: certs/cert.pem
      config:
        host: http://172.17.0.1:8080
        username: admin
        password: admin
    
    commands:
      config:
        api_path: /SEMP/v2/config
        module: solace_semp_config
        models: solace_semp_config.models
        api_class: MsgVpnApi
        config_class: Configuration
        client_class: ApiClient

    data_mappings:

See [https://github.com/unixunion/py-solace-provision/blob/master/solace.yaml](https://github.com/unixunion/py-solace-provision/blob/master/solace.yaml) for a full example.

If your version of the broker is greater than 9.3.0.0, it supports the SEMP `AllApi`, use that for `api_class` instead of 
`MsgVpnApi` to get control of even more configurations.


## Running

The yaml config needs to be mounted at a specific location inside the container.

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        unixunion/pysolpro:0.2.8-9.8.0.12 config --help

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        unixunion/pysolpro:0.2.8-9.8.0.12 config create_msg_vpn --help

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        unixunion/pysolpro:0.2.8-9.8.0.12 \
        config get_msg_vpns


## Yaml Data Files

Every solace managed object can be provisioned and updated from YAML data. The yaml data should be mounted into the 
container. e.g:

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        -v `pwd`/data:/data  unixunion/pysolpro:0.2.8-9.8.0.12 \
        config create_msg_vpn --body /data/vpn.yaml

### Yaml Examples

In order to create YAML [data](https://github.com/unixunion/py-solace-provision/tree/master/tests/testdata) files, simply 
query the appliance for the data. Note that some properties cannot be queried, such as credentials, and certificates.

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        -v `pwd`/data:/data  unixunion/pysolpro:0.2.8-9.8.0.12 \
        config get_msg_vpn --msg_vpn_name default

The output from the above can be saved to file, and used as body payload for CRUD operations. See Saving Yaml below.

Also see https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/msgVpn/createMsgVpn for
more information about what fields should be present.

### Saving Yaml

The option `--save` and `--save-dir` allow retrieved objects to write out to the savedir location. 

    docker run -v `pwd`/output:/savedata \
        -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        unixunion/pysolpro:0.2.8-9.8.0.12 \
            --save 
            --save-dir /savedata \
            config get_msg_vpn --msg_vpn_name default 

As mentioned above, some fields are not yet gettable, like secrets. 

### Data Mappings

When saving objects, they are organized into a tree structure, grouped by VPN, and "None" for global configs.

    savedata
    ├── None
    │   ├── CertAuthority
    │   │   └── myca.yaml
    │   ├── ClientCertAuthority
    │   │   └── test1.yaml
    │   └── DmrCluster
    │       └── mydmr.yaml
    └── myvpn2
        ├── MsgVpn
        │   └── myvpn2.yaml
        ├── MsgVpnAclProfile
        │   └── myacl.yaml
        ├── MsgVpnAclProfileClientConnectException
        │   └── f9599e2002afe4402974dd8e3dbcc9da8358dda47246d5298686dded.yaml
        ├── MsgVpnAclProfilePublishException
        │   └── e6b296e0d75e6ef6b4f331ce5aa675ce8a6b82fb8ea788f37b7afc8e.yaml
        ├── MsgVpnAclProfileSubscribeException
        │   └── f187b5be725653e82fb10b7a5008f03d0291f10f029eb838fbee09af.yaml
        ├── MsgVpnClientProfile
        │   └── some-profile.yaml
        └── MsgVpnQueue
            ├── another.queue.name.yaml
            └── testqueue.yaml


How these objects are named, is based on the data_mappings map in the config, which resolved Type to field within that type
to use as a file_name, or `hashfile` which hashes the payload.


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
        api_class: AllApi
        config_class: Configuration
        client_class: ApiClient
    data_mappings:
        ...

Run PySolPro

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        unixunion/pysolpro:0.2.8-9.8.0.12 \
        config get_msg_vpn \
            --msg_vpn_name default

Provision a Queue using a YAML file

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        -v `pwd`/data:/data  unixunion/pysolpro:0.2.8-9.8.0.12 \
        config create_msg_vpn_queue \
            --msg_vpn_name default --body /data/queue.yaml

Change the queue egress enabled state

    docker run -v `pwd`/solace.yaml:/opt/pysolpro/solace.yaml \
        -v `pwd`/data:/data unixunion/pysolpro:0.2.8-9.8.0.12 \
        config update_msg_vpn_queue \
            --msg_vpn_name default \
            --queue_name test \
            --body /data/queue.yaml \
            --override egressEnabled false


### Common Pitfalls

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

Versions before 9.3.0.0 of the broker do not have the AllApi, in these cases you will get an error like

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