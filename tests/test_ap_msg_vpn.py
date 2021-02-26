import argparse
import logging
import unittest
from unittest import TestCase

import solace_semp_action
import solace_semp_config
import solace_semp_monitor
from solace_semp_action import AllApi as ActionAllApi
from solace_semp_config import AllApi as ConfigAllApi
from solace_semp_monitor import AllApi as MonitorAllApi

from sp.AutoApi import AutoApi
from sp.DataPersist import DataPersist
from sp.SolaceResponseProcessor import SolaceResponseProcessor
from sp.util import get_client, generic_output_processor
from tests.common import bootstrap

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('solace-provision')
logger.setLevel(logging.INFO)

unittest.TestLoader.sortTestMethodsUsing = None


class TestApMsgVpn(TestCase):

    # parser
    parser = None
    aa = None

    def setUp(self):
        self.parser, self.aa = bootstrap()

    def test_a1_create_msg_vpn(self):
        args = self.parser.parse_args(['config', 'create_msg_vpn', '--body', 'testdata/myvpn2/MsgVpn/myvpn2.yaml'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
        assert ret.data.msg_vpn_name == "myvpn2"

    def test_a1_get_msg_vpn(self):
        args = self.parser.parse_args(['config', 'get_msg_vpn', '--msg_vpn_name', 'myvpn2'])
        ret = args.func(args)
        generic_output_processor(args.func, args, callback=SolaceResponseProcessor())
        assert ret.meta.response_code == 200

    def test_a1_get_msg_vpn_and_save(self):
        args = self.parser.parse_args(['config', 'get_msg_vpn', '--msg_vpn_name', 'myvpn2'])
        ret = args.func(args)
        generic_output_processor(args.func, args,
                                 callback=SolaceResponseProcessor(data_callback=DataPersist(save_data=True)))
        try:
            f = open("savedata/myvpn2/MsgVpn/myvpn2.yaml", "r")
        except Exception as e:
            raise

        assert ret.meta.response_code == 200

    def test_a1_override(self):
        args = self.parser.parse_args(['config', 'update_msg_vpn', '--msg_vpn_name', 'myvpn2',
                                       '--body', 'testdata/myvpn2/MsgVpn/myvpn2.yaml',
                                       '--override', 'enabled', 'false',
                                       '--override', 'dmrEnabled', 'false'])
        ret = args.func(args)
        logger.info(ret)
        assert ret.meta.response_code == 200
        assert ret.data.enabled is False

    def test_a2_delete(self):
        args = self.parser.parse_args(['config', 'delete_msg_vpn', '--msg_vpn_name', 'myvpn2'])
        ret = args.func(args)
        assert ret.meta.response_code == 200



