#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import logging
import sys

try:
    import coloredlogs
    coloredlogs.install()
except ImportError as e:
    pass

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger("solace-provision")
# logger.setLevel(logging.INFO)
# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter()
# handler.setFormatter(formatter)
# logger.addHandler(handler)

import argparse

from sp.ArgParseCache import ArgParserCache
from sp.SolaceResponseProcessor import SolaceResponseProcessor
from sp.util import PreserveWhiteSpaceWrapRawTextHelpFormatter, getClient, genericOutputProcessor

# populated at runtime
active_modules = []

# argparce cache holder
apc = None


# a generic data callback, for things like saving yaml
def arbitrary_data_callback(*args, **kwargs):
    for arg in args:
        logger.debug("arg: %s" % arg)
    logger.debug("kwargs: %s" % kwargs)

    if args[0]:
        # do something with the data
        # data = args[0]
        pass


if __name__ == '__main__':
    client_resolver = getClient

    parser = argparse.ArgumentParser(prog='pySolPro', formatter_class=PreserveWhiteSpaceWrapRawTextHelpFormatter)
    subparsers = parser.add_subparsers(help='sub-command help')

    # if tab-completion, use this
    # the argparse cache
    try:
        import argcomplete
        apc = ArgParserCache()
        subparsers = apc.create_subparsers_from_cache(subparsers)
        argcomplete.autocomplete(parser)
    except Exception as e:
        logger.error("auto complete error: %s" % e)
    finally:
        from sp.AutoManageGenerator import AutoManageGenerator

        # list of "plugins" to load
        sp_modules = [
            AutoManageGenerator
        ]

        logger.info("doing")

        [active_modules.append(m(subparsers, client_resolver)) for m in sp_modules]

        # maybe generate cache for argparse
        apc = ArgParserCache()
        apc.create_cache_from_parser(parser)

        args = parser.parse_args()
        from solace_semp_config.rest import ApiException

        if hasattr(args, "func"):
            try:
                genericOutputProcessor(args.func, args,
                                       callback=SolaceResponseProcessor(data_callback=arbitrary_data_callback))

            except ApiException as e:
                logger.error("error occurred %s" % e)
            except AttributeError as e:
                logger.error("attribute error %s" % e)
            except TypeError as e:
                logger.error("type error %s" % e)
            except Exception as e:
                parser.print_help()
        else:
            logger.info("please choose a sub-command")
            parser.print_help()
