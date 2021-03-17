#!/usr/bin/env python
import argparse
import os
import logging

import yaml

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''This python script scans through downloaded monitor API data for old message id's
    In order to run this, first...
        pysolpro.py --save --save-dir configdata config get_msg_vpns
        ls configdata/None/MsgVpn | xargs -I@ | sed 's/'.yaml//g | xargs -I@  echo pysolpro.py monitor get_msg_vpn_queues --msg_vpn_name @")''')
parser.add_argument("--dir", action="store", required=True, dest="dir")
parser.add_argument("--threshold", action="store", default=100000, dest="threshold")
parser.add_argument("--debug", default=False, action="store_true")
args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO, format='%(message)s')

try:
    import coloredlogs

    coloredlogs.install()
except ImportError as e:
    pass

highest_id_seen = 0

for root, dirs, files in os.walk(args.dir, topdown=False):
    for name in files:
        file = os.path.join(root, name)
        logging.debug("file: %s", file)
        with open(file) as f:
            try:
                queue_monitor_object = yaml.safe_load(f)
                last_spooled_msg_id = queue_monitor_object["lastSpooledMsgId"]
                if (last_spooled_msg_id > highest_id_seen):
                    highest_id_seen = last_spooled_msg_id
                lowest_msg_id = queue_monitor_object["lowestMsgId"]
                logging.debug("queueName: %s" % queue_monitor_object["queueName"])
                logging.debug("\tlowest: %s" % lowest_msg_id)
                logging.debug("\thighest: %s" % last_spooled_msg_id)
                delta = (last_spooled_msg_id - lowest_msg_id)
                logging.debug("\tdelta: %s" % delta)
                if (delta>args.threshold):
                    logging.warning("threshold violation for queue: %s, vpn: %s, owner: %s, oldest msgId: %s, "
                                    "lastest msgId: %s "
                                    % (queue_monitor_object["queueName"], queue_monitor_object["msgVpnName"],
                                       queue_monitor_object["owner"], lowest_msg_id, last_spooled_msg_id))
                    # logging.info("threshold violation for queue: %s, vpn: %s, owner: %s"
                    #                 % (queue_monitor_object["queueName"], queue_monitor_object["msgVpnName"],
                    #                    queue_monitor_object["owner"]))
            except Exception as e:
                pass