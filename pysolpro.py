#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s[%(filename)s:%(lineno)d->%(funcName)20s()] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

import argparse

from sp.ArgParseCache import ArgParserCache
from sp.SolaceResponseProcessor import SolaceResponseProcessor
from sp.util import PreserveWhiteSpaceWrapRawTextHelpFormatter, getClient, genericOutputProcessor

# try:
#     import argcomplete
#     # todo fixme, make the argcompletion use a cached version of the argparser namespaces
# except ModuleNotFoundError as e:
#     print("argcomplete is not available, tab completion disabled")


# populated at runtime
active_modules = []


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

    # if tab-completionoing, use this
    # the argparse cache
    try:
        import argcomplete
        apc = ArgParserCache()
        subparsers = apc.generate_parser(subparsers)
        argcomplete.autocomplete(parser)
    except Exception as e:
        logger.error("auto complete error: %s" % e)
    finally:
        from sp.AutoManageGenerator import AutoManageGenerator

        # list of "plugins" to load
        sp_modules = [
            AutoManageGenerator
        ]

        [active_modules.append(m(subparsers, client_resolver)) for m in sp_modules]

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
