#!/usr/bin/env python
import json
import os
import subprocess
import logging
import sys

"""
This python script configures DMR betwixt two local solace brokers.

"""

logging.basicConfig(level=logging.INFO)

if not os.path.isfile("pysolpro.py"):
    logging.error("run this from the root directory of project, e.g: python examples/provision_dmr.py")
    sys.exit(1)

broker1_config = "data/broker1.yaml"
broker2_config = "data/broker2.yaml"


# Get the ip addresses of the brokers
proc = subprocess.Popen(['docker', 'inspect', 'broker1'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
b1 = proc.communicate()[0].decode("UTF-8")
proc = subprocess.Popen(['docker', 'inspect', 'broker2'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
b2 = proc.communicate()[0].decode("UTF-8")
b1_inspect_data = json.loads(b1)
b1_ipaddress = b1_inspect_data[0]['NetworkSettings']['Networks']['solace-provision_default']['IPAddress']
b2_inspect_data = json.loads(b2)
b2_ipaddress = b2_inspect_data[0]['NetworkSettings']['Networks']['solace-provision_default']['IPAddress']
logging.info("broker1: %s" % b1_ipaddress)
logging.info("broker2: %s" % b2_ipaddress)


# broker1
os.environ["PYSOLPRO_CONFIG"] = broker1_config
os.system("./pysolpro.py config create_dmr_cluster --body data/broker1/dmr/dmr-cluster.yaml")
os.system("./pysolpro.py config create_dmr_cluster_link --dmr_cluster_name mydmr --body data/broker1/dmr/dmr-cluster-link/broker2.yaml")
os.system("./pysolpro.py config create_dmr_cluster_link_remote_address --dmr_cluster_name mydmr --remote_node_name broker2 --body data/broker1/dmr/dmr-cluster-link-remote/broker2.yaml --override remoteAddress {b2_ipaddress}".format(b2_ipaddress=b2_ipaddress))
os.system("./pysolpro.py config update_dmr_cluster_link --dmr_cluster_name mydmr --remote_node_name broker2 --body data/broker1/dmr/dmr-cluster-link/broker2.yaml --override enabled true")
os.system("./pysolpro.py config update_dmr_cluster --dmr_cluster_name mydmr --body data/broker1/dmr/dmr-cluster.yaml --override enabled true")


os.environ["PYSOLPRO_CONFIG"] = broker2_config
os.system("./pysolpro.py config create_dmr_cluster --body data/broker2/dmr/dmr-cluster.yaml")
os.system("./pysolpro.py config create_dmr_cluster_link --dmr_cluster_name mydmr --body data/broker2/dmr/dmr-cluster-link/broker1.yaml")
os.system("./pysolpro.py config create_dmr_cluster_link_remote_address --dmr_cluster_name mydmr --remote_node_name broker1 --body data/broker2/dmr/dmr-cluster-link-remote/broker1.yaml --override remoteAddress {b1_ipaddress}".format(b1_ipaddress=b1_ipaddress))
os.system("./pysolpro.py config update_dmr_cluster_link --dmr_cluster_name mydmr --remote_node_name broker1 --body data/broker2/dmr/dmr-cluster-link/broker1.yaml --override enabled true")
os.system("./pysolpro.py config update_dmr_cluster --dmr_cluster_name mydmr --body data/broker2/dmr/dmr-cluster.yaml --override enabled true")





