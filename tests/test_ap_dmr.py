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


class TestApDmr(TestCase):

    # parser
    parser = None
    aa = None

    def setUp(self):
        self.parser, self.aa = bootstrap()

    def test_b0_create_dmr_cluster(self):
        args = self.parser.parse_args(
            ['config', 'create_dmr_cluster', '--body', 'testdata/None/DmrCluster/mydmr.yaml'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
        assert ret.data.dmr_cluster_name == "mydmr"

    def test_b11_get_dmr_cluster_tls(self):
        myparser, myaa = bootstrap(tls=True)
        args = myparser.parse_args(
            ['--save', '--save-dir', 'savedir', 'config', 'get_dmr_cluster', '--dmr_cluster_name', 'mydmr', '--opaque_password', 'superssecreet'])
        ret = args.func(args)
        print(ret)
        assert ret.meta.response_code == 200
        assert ret.data.dmr_cluster_name == "mydmr"
        assert ret.data.authentication_basic_password != ''

    def test_b111_update_dmr_cluster_tls(self):
        myparser, myaa = bootstrap(tls=True)
        args = myparser.parse_args(
            ['config', 'update_dmr_cluster',
             '--dmr_cluster_name', 'mydmr',
             '--body', 'testdata/None/DmrCluster/mydmr-enc.yaml',
             '--opaque_password', 'superssecreet'])
        ret = args.func(args)
        print(ret)
        assert ret.meta.response_code == 200
        assert ret.data.dmr_cluster_name == "mydmr"
        assert ret.data.authentication_basic_password != None

    def test_b2_save_dmr_cluster(self):
        args = self.parser.parse_args(
            ['--save', 'config', 'get_dmr_cluster', '--dmr_cluster_name', 'mydmr'])
        try:
            os.remove("savedata/None/DmrCluster/mydmr.yaml")
        except Exception as e:
            pass
        assert os.path.isfile("savedata/None/DmrCluster/mydmr.yaml") is False
        ret = generic_output_processor(args.func, args,
                                       callback=SolaceResponseProcessor(
                                           data_callback=DataPersist(save_data=args.save, save_dir=args.savedir)))
        assert os.path.isfile("savedata/None/DmrCluster/mydmr.yaml") is True
        assert ret.meta.response_code == 200

    def test_b9_delete_dmr_cluster(self):
        args = self.parser.parse_args(
            ['config', 'delete_dmr_cluster', '--dmr_cluster_name', 'mydmr'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
