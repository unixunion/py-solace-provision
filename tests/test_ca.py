import logging
import logging
import os
import unittest
from unittest import TestCase

from sp.DataPersist import DataPersist
from sp.SolaceResponseProcessor import SolaceResponseProcessor
from sp.util import generic_output_processor
# fixme, if parser already has a subcommand in mind, then we dont need to import all of these
from tests.common import bootstrap

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('solace-provision')
logger.setLevel(logging.INFO)

unittest.TestLoader.sortTestMethodsUsing = None


class TestCA(TestCase):

    # parser
    parser = None
    aa = None

    def setUp(self):
        self.parser, self.aa = bootstrap()

    def test_b1_create_ca(self):
        args = self.parser.parse_args(
            ['config', 'create_cert_authority', '--body', 'testdata/None/CertAuthority/myca.yaml'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
        assert ret.data.cert_authority_name == "myca"

    def test_b2_create_caottc(self):
        args = self.parser.parse_args(
            ['config', 'create_cert_authority_ocsp_tls_trusted_common_name', '--body', 'testdata/None/CertAuthorityOcspTlsTrustedCommonName/foo.yaml', '--cert_authority_name', 'myca'])
        ret = args.func(args)
        assert ret.meta.response_code == 200
        assert ret.data.cert_authority_name == "myca"
        assert ret.data.ocsp_tls_trusted_common_name == "foo"

    def test_b3_delete_caottc(self):
        args = self.parser.parse_args(
            ['config', 'delete_cert_authority_ocsp_tls_trusted_common_name', '--ocsp_tls_trusted_common_name', 'foo', '--cert_authority_name', 'myca'])
        ret = args.func(args)
        assert ret.meta.response_code == 200

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
