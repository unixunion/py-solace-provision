#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import logging
import sys



logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("pysolpro")
logger.setLevel(logging.INFO)

try:
    import coloredlogs
    coloredlogs.install()
except ImportError as e:
    pass

# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter()
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# import sp.SettingsLoader as settings
# import libkplug
# from libksettings import KSettings/
# settings = KSettings(config_filename="solace.yaml", MY_HELLO_WORLD_CLASS='HelloWorldPlugin', PLUGINS=['sp.plugins.plugin_helloworld'], load_yaml=True)

logger.info("pysolpro: https://github.com/unixunion/py-solace-provision")

import sp

settings = sp.settings
from sp.DataPersist import DataPersist
from sp.SubCommandConfig import create_subcmd_config

import argparse

from sp.ArgParseCache import ArgParserCache
from sp.SolaceResponseProcessor import SolaceResponseProcessor
from sp.util import PreserveWhiteSpaceWrapRawTextHelpFormatter, get_client, generic_output_processor

# populated at runtime
active_modules = []

# argparse cache holder
apc = None

dp = DataPersist()


# a generic data callback, for things like saving yaml
def arbitrary_data_callback(*args, **kwargs):
    try:
        dp.save_object(*args)
    except Exception as e:
        logger.error("error saving object: %s" % e)
        raise


if __name__ == '__main__':
    client_resolver = get_client

    parser = argparse.ArgumentParser(prog='pySolPro', formatter_class=PreserveWhiteSpaceWrapRawTextHelpFormatter)
    parser.add_argument("--save", dest="save", action='store_true', default=False, help="save retrieved data to disk")
    parser.add_argument("--save-dir", dest="savedir", action="store", default="savedata", help="location to save to")
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
            # todo fixme this doesnt work since --save and --save-file added
            cmd = sys.argv[1:][0]
            if cmd:
                logger.debug("args %s" % sys.argv[1:])
                if cmd in settings.commands:
                    logger.debug("command match, limiting subparser init")

                    a = create_subcmd_config(cmd,
                                             settings.commands[cmd]["module"],
                                             settings.commands[cmd]["models"],
                                             settings.commands[cmd]["api_class"],
                                             settings.commands[cmd]["config_class"],
                                             settings.commands[cmd]["client_class"])
                    if a:
                        klasses = [a]

                    from sp.AutoApi import AutoApi

                    try:
                        from solace_semp_config.rest import ApiException
                    except ImportError as e:
                        logger.error(sp.solace_semp_unavailable_error)
                        raise

                    aa = AutoApi(subparsers, client_resolver, klasses=klasses)
                    args = parser.parse_args()
                    try:
                        generic_output_processor(args.func, args,
                                                 callback=SolaceResponseProcessor(
                                                     data_callback=DataPersist(save_data=args.save,
                                                                               save_dir=args.savedir)))
                    except ApiException as e:
                        logger.error("error occurred %s" % e)
                        sys.exit(1)
                    except AttributeError as e:
                        logger.error("attribute error %s, try adding --help" % e)
                        sys.exit(1)
                    except TypeError as e:
                        logger.error("type error %s" % e)
                        sys.exit(1)
                    except Exception as e:
                        logger.error("Exception: %s" % e)
                        parser.print_help()
                        sys.exit(1)

                    sys.exit(0)


        except Exception as e:
            logger.error("Error invoking performance optimized argparse %s" % e)
            pass

        logger.info("initializing all modules")

        # import this here because its slow, and we don't want to impede the autocompleter
        # from sp.AutoManageGenerator import AutoManageGenerator
        from sp.AutoApi import AutoApi

        logger.debug("done")

        # list of "plugins" to load
        sp_modules = [
            AutoApi
        ]

        klasses = []
        for cmd in settings.commands:
            logger.debug("init cmd: %s" % cmd)
            a = create_subcmd_config(cmd,
                                     settings.commands[cmd]["module"],
                                     settings.commands[cmd]["models"],
                                     settings.commands[cmd]["api_class"],
                                     settings.commands[cmd]["config_class"],
                                     settings.commands[cmd]["client_class"])
            if a:
                klasses.append(a)

        [active_modules.append(m(subparsers, client_resolver, klasses=klasses)) for m in sp_modules]
        # maybe generate cache for argparse
        if apc:
            apc.create_cache_from_parser(parser)

        args = parser.parse_args()
        try:
            from solace_semp_config.rest import ApiException
        except ImportError as e:
            logger.error(sp.solace_semp_unavailable_error)
            raise

        if hasattr(args, "func"):
            try:
                generic_output_processor(args.func, args,
                                         callback=SolaceResponseProcessor(
                                             data_callback=DataPersist(save_data=args.save, save_dir=args.savedir)))

            except ApiException as e:
                logger.error("error occurred %s" % e)
                sys.exit(1)
            except AttributeError as e:
                logger.error("attribute error %s, try adding --help" % e)
                sys.exit(1)
            except TypeError as e:
                logger.error("type error %s" % e)
                sys.exit(1)
            except Exception as e:
                parser.print_help()
                sys.exit(1)
        else:
            logger.info("please choose a sub-command")
            parser.print_help()
            sys.exit(1)
