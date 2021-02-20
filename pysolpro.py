#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import argparse
import logging
import sys

import yaml

try:
    import argcomplete
except ModuleNotFoundError as e:
    print("argcomplete is not available, tab completion disabled")

from sp.AutoManageGenerator import AutoManageGenerator
from sp.util import PreserveWhiteSpaceWrapRawTextHelpFormatter, getClient, genericOutputProcessor, \
    to_good_dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s[%(filename)s:%(lineno)d->%(funcName)20s()] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# list of "plugins" to load
sp_modules = [
    AutoManageGenerator
]

# populated at runtime
active_modules = []


class SolaceResponseProcessor:
    # a place to call with data payloads for example when you want to save to disk
    data_callback = None

    def __init__(self, data_callback=None):
        self.data_callback = data_callback

    def __call__(self, *args, **kwargs):
        for arg in args:
            logger.debug("arg: %s" % arg)
        logger.debug("kwargs: %s" % kwargs)

        data = args[0]

        if hasattr(data, "data"):
            logger.debug("data present")
            if (isinstance(data.data, list)):
                logger.debug("list response")
                for i in data.data:
                    y = yaml.dump(to_good_dict(i))
                    logger.info("response data\n%s" % y)
                    if self.data_callback:
                        self.data_callback(y, *args, **kwargs)
            else:
                logger.debug("single response")
                y = yaml.dump(to_good_dict(data.data))
                logger.info("response data\n%s" % y)
                if self.data_callback:
                    self.data_callback(y, *args, **kwargs)

        if hasattr(data, "meta"):
            logger.debug("meta is present")
            logger.info("response_code: %s" % data.meta.response_code)


# a generic data callback, for things like saving yaml
def arbitary_data_callback(*args, **kwargs):
    for arg in args:
        logger.debug("arg: %s" % arg)
    logger.debug("kwargs: %s" % kwargs)

    if args[0]:
        #do something with the data
        #logger.info("data callback \n%s" % args[0])
        pass


if __name__ == '__main__':
    client_resolver = getClient

    parser = argparse.ArgumentParser(prog='pySolPro', formatter_class=PreserveWhiteSpaceWrapRawTextHelpFormatter)
    subparsers = parser.add_subparsers(help='sub-command help')
    [active_modules.append(m(subparsers, client_resolver)) for m in sp_modules]
    try:
        argcomplete.autocomplete(parser)
    except Exception as e:
        pass
    args = parser.parse_args()
    from solace_semp_config.rest import ApiException

    if hasattr(args, "func"):
        try:
            genericOutputProcessor(args.func, args,
                                   callback=SolaceResponseProcessor(data_callback=arbitary_data_callback))

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
