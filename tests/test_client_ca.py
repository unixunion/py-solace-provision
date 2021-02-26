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
from tests.common import bootstrap

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('solace-provision')
logger.setLevel(logging.INFO)

unittest.TestLoader.sortTestMethodsUsing = None


class TestClientCA(TestCase):

    # parser
    parser = None
    aa = None

    def setUp(self):
        self.parser, self.aa = bootstrap()

    def test_a1_create_ca(self):
        args = self.parser.parse_args(
            ['config', 'create_cert_authority', '--body', 'testdata/None/CertAuthority/myca.yaml'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
        assert ret.data.cert_authority_name == "myca"

    def test_b1_create_cca(self):
        args = self.parser.parse_args(
            ['config', 'create_client_cert_authority', '--body', 'testdata/None/ClientCertAuthority/test1.yaml'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
        assert ret.data.cert_authority_name == "test1"

    def test_b2_update_cca(self):
        args = self.parser.parse_args(
            ['config', 'update_client_cert_authority', '--body', 'testdata/None/ClientCertAuthority/test1.yaml', '--cert_authority_name', 'test1', '--override', 'crlUrl', 'http://mycrl', '--override', 'revocationCheckEnabled', 'false'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
        assert ret.data.cert_authority_name == "test1"
        assert ret.data.crl_url == "http://mycrl"

    def test_b3_save_cca(self):
        args = self.parser.parse_args(
            ['--save', 'config', 'get_client_cert_authority', '--cert_authority_name', 'test1'])
        try:
            os.remove("savedata/None/ClientCertAuthority/test1.yaml")
        except Exception as e:
            pass
        assert os.path.isfile("savedata/None/ClientCertAuthority/test1.yaml") is False
        ret = generic_output_processor(args.func, args,
                                       callback=SolaceResponseProcessor(
                                           data_callback=DataPersist(save_data=args.save, save_dir=args.savedir)))
        assert os.path.isfile("savedata/None/ClientCertAuthority/test1.yaml") is True
        assert ret.meta.response_code == 200

    def test_b8_delete_cca(self):
        args = self.parser.parse_args(
            ['config', 'delete_client_cert_authority', '--cert_authority_name', 'test1'])
        ret = args.func(args)
        assert ret.meta.response_code == 200

    def test_b9_delete_ca(self):
        args = self.parser.parse_args(
            ['config', 'delete_cert_authority', '--cert_authority_name', 'myca'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
