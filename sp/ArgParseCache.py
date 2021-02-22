import logging
import pickle
from argparse import ArgumentParser

logger = logging.getLogger('solace-provision')
logger.debug("imported")


class ArgParserCache:
    loaded = False
    subparsers = {}
    cache = {}
    cache_file_name = None

    def __init__(self, do_load=True, cache_file_name="pysolpro.cache"):
        """
        Instantiate a instance of the argparse cache, if it finds the cache_file on disk, it will load it.

        @param do_load: supress loading from disk
        @param cache_file_name: the file name to load, default "pysolpro.cache"

        """
        # check if cache is on disk, and load it, otherwise set loaded state to false
        self.cache_file_name = cache_file_name

        if do_load:
            try:
                with open(self.cache_file_name, mode='rb') as f:
                    logger.debug("loading cache")
                    self.cache = pickle.load(f)
                    self.loaded = True
            except FileNotFoundError as e:
                pass

    def create_cache_from_parser(self, parser: ArgumentParser):
        """
        If the cache has not been read from disk, populates the cache from parser, call save_cache to save it.

        @param parser: the parser instance to create a cache out of
        @return:
        """

        if self.loaded:
            return

        data = {}

        try:
            logger.info("populating cache from parser")
            t = parser._actions[1].choices
            for subcommand in t:
                data[subcommand] = {}
                choices = t[subcommand]._actions[1].choices
                for choice in choices:
                    logger.debug(choice)
                    data[subcommand][choice] = []
                    for opt in choices[choice]._actions:
                        if opt.option_strings[0] != "-h":
                            data[subcommand][choice].append((opt.option_strings[0], opt.dest, opt.help, 'str'))

            with open(self.cache_file_name, mode="wb") as f:
                pickle.dump(data, f)
                f.close()


        except Exception as e:
            logger.error("error: %s" % e)

    def create_subparsers_from_cache(self, subparser):
        """
        Read through the cache and create the subparsers

        @param subparser: The subparser to populate from the cache
        @return: the subparser
        """
        for subcommand in self.cache:
            logger.debug("sc: %s" % subcommand)
            subc = subparser.add_parser(subcommand).add_subparsers()

            for cmd in self.cache[subcommand]:
                logger.debug(cmd)
                tmp_group = subc.add_parser(cmd)
                # todo fixme only supports single argument name, not the list of long --name and short -n
                for param in self.cache[subcommand][cmd]:
                    if param[0] != "-h":
                        t = param
                        opt = "%s" % t[0]
                        help = t[2]
                        y = tmp_group.add_argument(opt, action="store", type=str, help=help)

        return subparser

    # def save_cache(self):
    #     """
    #     Generate the cache file from the subparser
    #     """
    #     if not self.loaded:
    #         for command in self.subparsers:
    #             self.cache[command] = []
    #             for choice in self.subparsers[command]["subparser"].choices:
    #
    #                 tmp = self.subparsers[command]["subparser"].choices[choice]
    #                 actions = []
    #                 for a in tmp._actions:
    #                     option_strings = a.option_strings
    #                     dest = a.dest
    #                     help = a.help
    #                     type = 'str'  # todo fixme this is hard-wired to string for now
    #                     actions.append((option_strings, dest, help, type))
    #                 self.cache[command].append({"command": choice, "action": actions})
    #         logger.debug("cache generated")
    #         with open(self.cache_file_name, mode="wb") as f:
    #             pickle.dump(self.cache, f)
    #             f.close()

    # def generate_parser(self, subparser):
    #     for subcommand in self.cache:
    #         logger.debug("sc: %s" % subcommand)
    #         subc = subparser.add_parser(subcommand).add_subparsers()
    #
    #         for cmd in self.cache[subcommand]:
    #             logger.debug(cmd)
    #             tmp_group = subc.add_parser(cmd["command"])
    #             # todo fixme only supports single argument name, not the list of long --name and short -n
    #             for param in cmd["action"]:
    #                 if param[0][0] != "-h":
    #                     t = param
    #                     opt = "%s" % t[0][0]
    #                     help = t[2]
    #                     y = tmp_group.add_argument(opt, action="store", type=str, help=help)
    #
    #     return subparser

    # def add_parser(self, command, method_name, help):
    #     self.subparsers[command]["data"][method_name] = {"method_name": method_name, "help": help, "default": {}}
    #
    # def add_default(self, command, callback, method_name):
    #     logger.info("command: %s. callback: %s, method_name: %s" % (command, callback, method_name))
    #     self.subparsers[command]["data"][method_name]["default"] = (command, callback, method_name)
