import argparse
import logging
import unittest
from unittest import TestCase

import solace_semp_config

from sp.AutoManageGenerator import AutoManageGenerator
from sp.legacy.common import gen_creds, http_semp_request
from sp.util import getClient

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('solace-provision')
logger.setLevel(logging.INFO)

unittest.TestLoader.sortTestMethodsUsing = None

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
        client = getClient

        self.parser = argparse.ArgumentParser(prog='pySolPro')
        subparsers = self.parser.add_subparsers(help='sub-command help')
        [self.active_modules.append(m(subparsers, client)) for m in self.sp_modules]

    def test_a1_create_msg_vpn(self):
        args = self.parser.parse_args(['config', 'create_msg_vpn', '--body', '../data/vpn.yaml'])
        ret = args.func(args)
        assert ret.meta.response_code == 200

    def test_a2_override(self):
        args = self.parser.parse_args(['config', 'update_msg_vpn', '--msg_vpn_name', 'myvpn2',
                                       '--body','../data/vpn.yaml',
                                       '--override', 'enabled', 'false',
                                       '--override', 'dmrEnabled', 'false'])
        ret = args.func(args)
        logger.info(ret)
        assert ret.meta.response_code == 200

    def test_delete(self):
        args = self.parser.parse_args(['config', 'delete_msg_vpn', '--msg_vpn_name', 'default'])
        ret = args.func(args)
        assert ret.meta.response_code == 200

    def test_z_delete_legacy(self):

        client = getClient("config", client_class=solace_semp_config.ApiClient, config_class=solace_semp_config.Configuration)

        semp_request = """
        <rpc semp-version="soltr/9_0_1VMR">
            <no>
                <message-vpn>
                    <vpn-name>%s</vpn-name>
                </message-vpn>
            </no>
        </rpc>""" % "myvpn2"
        cred, headers = gen_creds(client.configuration.username, client.configuration.password)
        return http_semp_request(client.configuration.host.split("/SEMP")[0], headers, semp_request, None)
