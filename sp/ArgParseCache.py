import argparse
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

    data_from_parser = {}

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
            logger.info("saving cache to disk")
            # get the "subparser"
            for p in parser._actions:
                if isinstance(p, argparse._SubParsersAction):

                    t = p.choices
                    for subcommand in t:
                        data[subcommand] = {}
                        for spa in t[subcommand]._actions:
                            if not isinstance(spa, argparse._HelpAction):
                                choices = spa.choices
                                for choice in choices:
                                    logger.debug(choice)
                                    data[subcommand][choice] = []
                                    for opt in choices[choice]._actions:
                                        if opt.option_strings[0] != "-h":
                                            data[subcommand][choice].append((opt.option_strings[0], opt.dest, opt.help, 'str'))

                    self.data_from_parser = data
                    with open(self.cache_file_name, mode="wb") as f:
                        pickle.dump(data, f)
                        f.close()


        except Exception as e:
            logger.error("error: %s" % e)
            raise

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

    def get_data_from_parser(self):
        return self.data_from_parser
