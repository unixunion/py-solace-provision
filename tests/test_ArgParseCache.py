import argparse
import unittest
from pathlib import Path
from unittest import TestCase

from sp.ArgParseCache import ArgParserCache

unittest.TestLoader.sortTestMethodsUsing = None


def void():
    pass


class TestArgParserCache(TestCase):
    apc = ArgParserCache(do_load=False, cache_file_name="test.cache")

    def test_create_cache_from_parser(self):
        parser = argparse.ArgumentParser(prog='pySolPro')
        subparsers = parser.add_subparsers(help='sub-command help')
        x = subparsers.add_parser("x", help="y").add_subparsers()
        x = x.add_parser("m")
        x.set_defaults(function=void())
        x.add_argument("--foo", action="store", type=str, help="foo help")
        x.add_argument("--bar", action="store", type=str, help="bar help")
        z = subparsers.add_parser("y", help="s").add_subparsers()
        z = z.add_parser("h")
        z.set_defaults(function=void())
        z.add_argument("--bar", action="store", help="bar help")
        z.add_argument("--baz", action="store", help="baz help")
        self.apc.create_cache_from_parser(parser)
        assert isinstance(self.apc.get_cache(), dict)
        print(self.apc.get_cache)
        assert self.apc.get_cache()["x"] == {
            'm': [('--foo', 'foo', 'foo help', 'str'), ('--bar', 'bar', 'bar help', 'str')]}


    def test_create_subparsers_from_cache(self):
        self.apc = ArgParserCache(do_load=True, cache_file_name="test.cache")
        assert self.apc.loaded is True
        parser = argparse.ArgumentParser(prog='pySolPro')
        subparsers = parser.add_subparsers(help='sub-command help')
        subparsers = self.apc.create_subparsers_from_cache(subparsers)
        assert len(subparsers.choices) == 2

    def test_z_cleanup(self):
        import os
        try:
            os.remove("test.cache")
        except Exception as e:
            raise
