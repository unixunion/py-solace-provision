import argparse
import logging
from unittest import TestCase

import solace_semp_client

from sp.AutoManageGenerator import AutoManageGenerator
from tests.commontest import getClient

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('solace-provision')
logger.setLevel(logging.INFO)


class TestApMsgVpn(TestCase):
    # list of "plugins" to load
    sp_modules = [
        AutoManageGenerator
    ]

    # populated at runtime
    active_modules = []

    # parser
    parser = None

    def setUp(self):
        client = getClient()
        api = solace_semp_client.MsgVpnApi(api_client=client)

        self.parser = argparse.ArgumentParser(prog='pySolPro')
        subparsers = self.parser.add_subparsers(help='sub-command help')
        [self.active_modules.append(m(subparsers, client)) for m in self.sp_modules]
        # args = self.parser.parse_args()
        # try:
        #     args.func(args)
        # except Exception as e:
        #     self.parser.print_help()

    def test_delete(self):
        args = self.parser.parse_args(['delete_msg_vpn', '--msg_vpn_name', 'default'])
        ret = args.func(args)
        assert ret == 200
