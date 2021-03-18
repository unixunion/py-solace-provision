import argparse
import logging
import pickle
import re
from argparse import ArgumentParser
from pathlib import Path
import sp

logger = logging.getLogger('pysolpro')
logger.debug("imported")


class ArgParserCache:
    loaded = False
    subparsers = {}
    cache = {}
    cache_file_name = None

    data_from_parser = {}

    version = '0.3.0'

    def __init__(self, do_load=True, cache_file_name="%s/.pysolpro/%s" % (Path.home(), sp.settings.cache_file_name)):
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

        # the meta, and choices is initialized
        data = {"meta": {"version": self.version}, "choices_db": {}}

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
                                    logger.debug("method: %s" % choice)
                                    data[subcommand][choice] = []
                                    for opt in choices[choice]._actions:
                                        if opt.option_strings[0] != "-h":
                                            data[subcommand][choice].append(
                                                (opt.option_strings[0], opt.dest, opt.help, 'str'))

                    # self.data_from_parser = data
                    self.cache = data
                    self.save()
                    # try:
                    #     with open(self.cache_file_name, mode="wb") as f:
                    #         pickle.dump(data, f)
                    #         f.close()
                    # except Exception as e:
                    #     logger.warning("unable to initialize cache file: %s" % e)


        except Exception as e:
            logger.error("error: %s" % e)
            raise

    def save(self):
        try:
            logger.debug("cache: %s" % self.cache)
            logger.debug("saving to file: %s" % self.cache_file_name)
            with open(self.cache_file_name, mode="wb") as f:
                pickle.dump(self.cache, f)
                f.close()
        except Exception as e:
            logger.warning("unable to initialize cache file: %s" % e)

    def create_subparsers_from_cache(self, subparser):
        """
        Read through the cache and create the subparsers

        @param subparser: The subparser to populate from the cache
        @return: the subparser
        """

        for subcommand in self.cache:
            if subcommand == "meta":
                if self.cache[subcommand]["version"] == self.version:
                    logger.debug("apc version check: ok")
                else:
                    logger.warning("argparse cache is from different version, please delete ~/.pysolpro/pysolpro.cache")
                logger.debug("ignoring meta: %s" % subcommand)
            elif subcommand == "choices_db":
                logger.debug("loading choices_db")

            else:
                logger.debug("subcommand: %s" % subcommand)
                subc = subparser.add_parser(subcommand).add_subparsers()

                for cmd in self.cache[subcommand]:
                    logger.debug("method: %s" % cmd)
                    tmp_group = subc.add_parser(cmd)
                    # todo fixme only supports single argument name, not the list of long --name and short -n
                    for param in self.cache[subcommand][cmd]:
                        if param[0] != "-h":
                            t = param
                            logger.debug("param: %s" % t[0])
                            opt = "%s" % t[0]
                            help = t[2]
                            y = tmp_group.add_argument(opt, action="store", type=str, help=help, choices=self.make_choices(t[1]))

        logger.debug(self.cache)
        return subparser

    def get_data_from_parser(self):
        return self.data_from_parser

    def is_loaded(self):
        return self.loaded

    def make_choices(self, method):
        logger.debug("make_choices: %s" % method)
        if method in self.cache["choices_db"]:
            return self.cache["choices_db"][method]
        else:
            logger.debug("default")
            return ["__incomplete__"]

    def update_choices(self, x, t, *y, **kwargs):
        logger.debug("called with: %s" % x)
        logger.debug(t.func.get_target())

        logger.debug(y)
        # z = t.func.get_target()
        method_name = t.func.get_target().__name__
        logger.debug("method_name: %s" % method_name)

        return_type = self.get_return_type_for_method_docs_strings(t.func.get_target())
        logger.debug(return_type)

        import sp
        object_name_mappings = sp.settings.data_mappings
        try:
            name_field = object_name_mappings[return_type]
            logger.debug("name field: %s" % name_field)
            if isinstance(y[0].data, list):
                for i in y[0].data:
                    self.append_choices(name_field, getattr(i, name_field))
            else:
                self.append_choices(name_field, getattr(y[0].data, name_field))
            logger.debug(self.cache["choices_db"])
            self.save()
        except Exception as e:
            logger.error(e)
            logger.debug("unable to update choices cache, no mapping for %s, please add a mapping to yaml config "
                           "for which field names this object, e.g: MsgVpnsResponse: msgVpnName" % return_type)
        # logger.info(y)
        # logger.info(kwargs)

    def append_choices(self, method, choice):
        if method in self.cache["choices_db"]:
            if not choice in self.cache["choices_db"][method]:
                logger.debug("updating")
                self.cache["choices_db"][method].append(choice)
        else:
            self.cache["choices_db"][method] = [choice]

    # gets all the types from the parameters in the docstrings
    def get_return_type_for_method_docs_strings(self, method):
        if hasattr(method, "__doc__"):
            try:
                type_name = re.search(':return: (\w+?)\n', method.__doc__)
                logger.debug(type_name)
                return type_name.group(1)
            except Exception as e:
                return None