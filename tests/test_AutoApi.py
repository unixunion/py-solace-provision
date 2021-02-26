import argparse
from unittest import TestCase

from solace_semp_config import MsgVpnApi, ApiClient

from sp.AutoApi import AutoApi
from tests.common import bootstrap


class TestAutoApi(TestCase):

    # parser
    parser = None
    aa = None

    def setUp(self):
        self.parser, self.aa = bootstrap()

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
        aa = self.aa  # type: AutoApi
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





