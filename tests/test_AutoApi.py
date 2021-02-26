import argparse
from unittest import TestCase

import solace_semp_config
from solace_semp_config import MsgVpnApi, ApiClient

from sp.AutoApi import AutoApi
from sp.util import get_client


klasses = [
    {
        "api": MsgVpnApi,
        "models": "solace_semp_config.models",
        "subcommand": "config",
        "config_class": solace_semp_config.Configuration,
        "client_class": solace_semp_config.ApiClient
    }
]


class TestAutoApi(TestCase):

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

    def simple_method(self, a1, a2, k1=1, k2=2):
        """

        @param str a1:
        @param str a2:
        @param int k1:
        @param int k2:
        @param int k3:
        @return:
        """
        pass

    def test_get_all_param_types_from_method(self):
        aa = self.active_modules[0] # type: AutoApi
        f = aa.get_all_param_types_from_method(self.simple_method)
        assert isinstance(f, list)
        assert len(f) == 9

    def test_auto_sub_command_arg_parser(self):
        parser = argparse.ArgumentParser(prog='pySolPro')
        subparsers = parser.add_subparsers(help='sub-command help')
        AutoApi.auto_sub_command_arg_parser(subparsers,
                                                           models="solace_semp_monitor.models",
                                                           apiclass=MsgVpnApi,
                                                           callback=MsgVpnApi(api_client=ApiClient()))
        assert len(subparsers.choices) > 10





