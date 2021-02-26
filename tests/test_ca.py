import argparse
import logging
import unittest
from unittest import TestCase
import os

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


class TestCA(TestCase):
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
        self.parser.add_argument("--save", dest="save", action='store_true', default=False,
                                 help="save retrieved data to disk")
        self.parser.add_argument("--save-dir", dest="savedir", action="store", default="savedata",
                                 help="location to save to")
        subparsers = self.parser.add_subparsers(help='sub-command help')
        [self.active_modules.append(m(subparsers, client, klasses=klasses)) for m in self.sp_modules]

    def test_b1_create_ca(self):
        args = self.parser.parse_args(
            ['config', 'create_cert_authority', '--body', 'testdata/None/CertAuthority/myca.yaml'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
        assert ret.data.cert_authority_name == "myca"

    def test_b2_update_ca(self):
        args = self.parser.parse_args(
            ['config', 'update_cert_authority', '--body', 'testdata/None/CertAuthority/myca.yaml', '--cert_authority_name', 'myca', '--override', 'crlUrl', 'http://mycrl'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
        assert ret.data.cert_authority_name == "myca"
        assert ret.data.crl_url == "http://mycrl"

    def test_b3_save_ca(self):
        args = self.parser.parse_args(
            ['--save', 'config', 'get_cert_authority', '--cert_authority_name', 'myca'])
        try:
            os.remove("savedata/None/CertAuthority/myca.yaml")
        except Exception as e:
            pass
        assert os.path.isfile("savedata/None/CertAuthority/myca.yaml") is False
        ret = generic_output_processor(args.func, args,
                                       callback=SolaceResponseProcessor(
                                           data_callback=DataPersist(save_data=args.save, save_dir=args.savedir)))
        assert os.path.isfile("savedata/None/CertAuthority/myca.yaml") is True
        assert ret.meta.response_code == 200

    def test_b9_delete_ca(self):
        args = self.parser.parse_args(
            ['config', 'delete_cert_authority', '--cert_authority_name', 'myca'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
