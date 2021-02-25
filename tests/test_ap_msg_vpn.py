import argparse
import logging
import unittest
from unittest import TestCase

from pysolpro import arbitrary_data_callback
from sp.AutoApi import AutoApi
from sp.DataPersist import DataPersist
from sp.SolaceResponseProcessor import SolaceResponseProcessor
from sp.util import get_client, generic_output_processor

import solace_semp_action
import solace_semp_config
import solace_semp_monitor
from solace_semp_action import AllApi as ActionAllApi
from solace_semp_config import AllApi as ConfigAllApi
from solace_semp_monitor import AllApi as MonitorAllApi

# fixme, if parser already has a subcommand in mind, then we dont need to import all of these
klasses = [
    {
        "api": ConfigAllApi,
        "models": "solace_semp_config.models",
        "subcommand": "config",
        "config_class": solace_semp_config.Configuration,
        "client_class": solace_semp_config.ApiClient
    },
    {
        "api": MonitorAllApi,
        "models": "solace_semp_monitor.models",
        "subcommand": "monitor",
        "config_class": solace_semp_monitor.Configuration,
        "client_class": solace_semp_monitor.ApiClient
    },
    {
        "api": ActionAllApi,
        "models": "solace_semp_action.models",
        "subcommand": "action",
        "config_class": solace_semp_action.Configuration,
        "client_class": solace_semp_action.ApiClient
    }
]

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('solace-provision')
logger.setLevel(logging.INFO)

unittest.TestLoader.sortTestMethodsUsing = None


class TestApMsgVpn(TestCase):
    # list of "plugins" to load
    sp_modules = [
        AutoApi
    ]

    # populated at runtime
    active_modules = []

    # parser
    parser = None

    def setUp(self):
        client = get_client

        self.parser = argparse.ArgumentParser(prog='pySolPro')
        subparsers = self.parser.add_subparsers(help='sub-command help')
        [self.active_modules.append(m(subparsers, client, klasses=klasses)) for m in self.sp_modules]

    def test_a1_create_msg_vpn(self):
        args = self.parser.parse_args(['config', 'create_msg_vpn', '--body', '../data/vpn.yaml'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
        assert ret.data.msg_vpn_name == "myvpn2"

    def test_a1_get_msg_vpn_and_save(self):
        args = self.parser.parse_args(['config', 'get_msg_vpn', '--msg_vpn_name', 'myvpn2'])
        ret = args.func(args)
        generic_output_processor(args.func, args,
                                 callback=SolaceResponseProcessor(data_callback=DataPersist(save_data=True)))
        assert ret.meta.response_code == 200

    def test_a2_override(self):
        args = self.parser.parse_args(['config', 'update_msg_vpn', '--msg_vpn_name', 'myvpn2',
                                       '--body', '../data/vpn.yaml',
                                       '--override', 'enabled', 'false',
                                       '--override', 'dmrEnabled', 'false'])
        ret = args.func(args)
        logger.info(ret)
        assert ret.meta.response_code == 200

    def test_delete(self):
        args = self.parser.parse_args(['config', 'delete_msg_vpn', '--msg_vpn_name', 'myvpn2'])
        ret = args.func(args)
        assert ret.meta.response_code == 200

