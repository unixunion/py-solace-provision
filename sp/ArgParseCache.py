import logging
import pickle

logger = logging.getLogger('solace-provision')
logger.debug("imported")


class ArgParserCache:
    loaded = False

    subparsers = {}
    cache = {}
    cache_file_name = "pySolPro.cache"

    def __init__(self, do_load=True):
        # check if cache is on disk, and load it, otherwise set loaded state to false
        if do_load:
            with open(self.cache_file_name, mode='rb') as f:
                logger.debug("loading cache")
                self.cache = pickle.load(f)
                self.loaded = True

    # def add_sub_command(self, subcommand):
    #     self.subcommands.append(subcommand)

    def is_loaded(self):
        return self.loaded

    def add_subparser(self, command, subparsers):
        if not self.loaded:
            self.subparsers[command] = {"subparser": subparsers}

    def get_subparsers(self, command):
        if not self.loaded:
            return self.subparsers[command]["subparser"]

    def make_cache(self):
        if not self.loaded:
            for command in self.subparsers:
                self.cache[command] = []
                for choice in self.subparsers[command]["subparser"].choices:

                    tmp = self.subparsers[command]["subparser"].choices[choice]
                    actions = []
                    for a in tmp._actions:
                        option_strings = a.option_strings
                        dest = a.dest
                        help = a.help
                        type = 'str'  # todo fixme this is hard-wired to string for now
                        actions.append((option_strings, dest, help, type))
                    self.cache[command].append({"command": choice, "action": actions})
            logger.debug("cache generated")
            with open(self.cache_file_name, mode="wb") as f:
                pickle.dump(self.cache, f)
                f.close()

    def generate_parser(self, subparser):
        for subcommand in self.cache:
            logger.debug("sc: %s" % subcommand)
            subc = subparser.add_parser(subcommand).add_subparsers()

            for cmd in self.cache[subcommand]:
                logger.debug(cmd)
                tmp_group = subc.add_parser(cmd["command"])
                # todo fixme only supports single argument name, not the list of long --name and short -n
                for param in cmd["action"]:
                    if param[0][0] != "-h":
                        t = param
                        opt = "%s" % t[0][0]
                        help = t[2]
                        y = tmp_group.add_argument(opt, action="store", type=str, help=help)

        return subparser

    # def add_parser(self, command, method_name, help):
    #     self.subparsers[command]["data"][method_name] = {"method_name": method_name, "help": help, "default": {}}
    #
    # def add_default(self, command, callback, method_name):
    #     logger.info("command: %s. callback: %s, method_name: %s" % (command, callback, method_name))
    #     self.subparsers[command]["data"][method_name]["default"] = (command, callback, method_name)