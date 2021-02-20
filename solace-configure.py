#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import argparse
import logging
import sys

try:
    import argcomplete
except ModuleNotFoundError as e:
    print("argcomplete is not available, tab completion disabled")

from sp.AutoManageGenerator import AutoManageGenerator
from sp.util import PreserveWhiteSpaceWrapRawTextHelpFormatter, processOutput, getClient

import sp.settingsloader as settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# list of "plugins" to load
sp_modules = [
    AutoManageGenerator
]

# populated at runtime
active_modules = []

if __name__ == '__main__':
    client = getClient(settings=settings)

    parser = argparse.ArgumentParser(prog='pySolPro', formatter_class=PreserveWhiteSpaceWrapRawTextHelpFormatter)
    subparsers = parser.add_subparsers(help='sub-command help')
    [active_modules.append(m(subparsers, client)) for m in sp_modules]
    try:
        argcomplete.autocomplete(parser)
    except Exception as e:
        pass
    args = parser.parse_args()
    from solace_semp_client.rest import ApiException
    if hasattr(args, "func"):
        try:
            processOutput(args.func, args)

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
