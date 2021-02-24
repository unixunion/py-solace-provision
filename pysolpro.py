#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import logging
import sys

from sp.SubCommandConfig import create_subcmd_config

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

import sp.SettingsLoader as settings
import argparse

from sp.ArgParseCache import ArgParserCache
from sp.SolaceResponseProcessor import SolaceResponseProcessor
from sp.util import PreserveWhiteSpaceWrapRawTextHelpFormatter, get_client, generic_output_processor

# populated at runtime
active_modules = []

# argparse cache holder
apc = None


# a generic data callback, for things like saving yaml
def arbitrary_data_callback(*args, **kwargs):
    for arg in args:
        logger.debug("arg: %s" % arg)
    logger.debug("kwargs: %s" % kwargs)

    if args[0]:
        logger.debug("data process: %s" % args[0])
        pass


if __name__ == '__main__':
    client_resolver = get_client

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
        logger.warning("auto complete not installed, tab completion disabled")
    finally:

        try:
            cmd = sys.argv[1:][0]
            if cmd:
                logger.debug("args %s" % sys.argv[1:])
                if cmd in settings.commands:
                    logger.debug("command match, limiting subparser init")

                    klasses = [create_subcmd_config(cmd,
                                                    settings.commands[cmd]["module"],
                                                    settings.commands[cmd]["api_class"],
                                                    settings.commands[cmd]["config_class"],
                                                    settings.commands[cmd]["client_class"])]

                    from sp.AutoApi import AutoApi
                    from solace_semp_config.rest import ApiException

                    aa = AutoApi(subparsers, client_resolver, klasses=klasses)
                    args = parser.parse_args()
                    try:
                        generic_output_processor(args.func, args,
                                                 callback=SolaceResponseProcessor(data_callback=arbitrary_data_callback))
                    except ApiException as e:
                        logger.error("error occurred %s" % e)
                    except AttributeError as e:
                        logger.error("attribute error %s, try adding --help" % e)
                    except TypeError as e:
                        logger.error("type error %s" % e)
                    except Exception as e:
                        logger.error("Exception: %s" % e)
                        parser.print_help()

                    sys.exit(0)


        except Exception as e:
            logger.error("Error invoking performance optimized argparse %s" % e)
            pass

        logger.info("initializing all modules")

        # import this here because its slow, and we don't want to impede the autocompleter
        # from sp.AutoManageGenerator import AutoManageGenerator
        from sp.AutoApi import AutoApi

        # list of "plugins" to load
        sp_modules = [
            AutoApi
        ]

        klasses = []
        for cmd in settings.commands:
            klasses.append(create_subcmd_config(cmd,
                                                settings.commands[cmd]["module"],
                                                settings.commands[cmd]["api_class"],
                                                settings.commands[cmd]["config_class"],
                                                settings.commands[cmd]["client_class"]))

        [active_modules.append(m(subparsers, client_resolver, klasses=klasses)) for m in sp_modules]
        # maybe generate cache for argparse
        if apc:
            apc.create_cache_from_parser(parser)

        args = parser.parse_args()
        from solace_semp_config.rest import ApiException

        if hasattr(args, "func"):
            try:
                generic_output_processor(args.func, args,
                                         callback=SolaceResponseProcessor(data_callback=arbitrary_data_callback))

            except ApiException as e:
                logger.error("error occurred %s" % e)
            except AttributeError as e:
                logger.error("attribute error %s, try adding --help" % e)
            except TypeError as e:
                logger.error("type error %s" % e)
            except Exception as e:
                parser.print_help()
        else:
            logger.info("please choose a sub-command")
            parser.print_help()
