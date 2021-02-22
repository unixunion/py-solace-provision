import inspect
import logging

from sp.ArgParseCache import ArgParserCache
from sp.CallProxy import CallProxy
from sp.util import get_type_param_from_doc_strings, is_primitive

logger = logging.getLogger('solace-provision')


class AutoApi(object):

    parsers = []

    def __init__(self, subparsers, client_resolver, klasses=[]):
        """
        Generates argparser, and binds to methods it scans in the klasses list.

        @param subparsers: the subparser to associate commands with, must be a subparser of parser.
        @param client_resolver: the method used to resolve which client to use
        @param klasses: a list of modules, classes and apis scan
        """
        self.arg_parser_cache = ArgParserCache(do_load=False)

        if subparsers:
            for provider_api in klasses:
                subp = subparsers.add_parser(provider_api["subcommand"]).add_subparsers()
                self.parsers.append(AutoApi.auto_sub_command_arg_parser(subparsers=subp,
                                                                        command=provider_api["subcommand"],
                                                                        apiclass=provider_api["api"],
                                                                        arg_parser_cache=self.arg_parser_cache,
                                                                        callback=provider_api["api"](
                                                                            api_client=client_resolver(
                                                                                subcommand=provider_api[
                                                                                    "subcommand"],
                                                                                config_class=provider_api[
                                                                                    "config_class"],
                                                                                client_class=provider_api[
                                                                                    "client_class"]
                                                                            )
                                                                        )))

                logger.debug("loaded")

    # this is not yet used, it will be used to parse doc strings
    # for additional kwargs not identified in the signature
    # scan the sig, create list of values
    # scan the doc strings, where a param is found not in the list, add it as a kwarg
    @staticmethod
    def getArgsForMethod(apiclass, method_name):
        params = []
        # get the signature of the method
        sig = inspect.signature(getattr(apiclass, method_name))

        # for each parameter, check its type, and add to the subparsers as needed
        for param in sig.parameters.values():
            params.append(param.name)

        logger.debug("found params in method %s" % method_name)
        logger.debug(params)

    # dynamically create the argparser command line options at runtime
    @staticmethod
    def auto_sub_command_arg_parser(subparsers=None, command=None, apiclass=None, callback=None, arg_parser_cache=None):

        logger.debug("cache is not loaded, getting methods")
        object_methods = [method_name for method_name in dir(apiclass)
                          if callable(getattr(apiclass, method_name)) and not method_name.startswith(
                "__") and not method_name.endswith("with_http_info")]
        logger.debug("got methods")

        logger.debug(object_methods)

        # holder for groups
        groups = []

        for method_name in object_methods:
            logger.debug("method: %s " % method_name)

            # create the "method" subparser, sucking the dock strings into the help kwarg
            tmpGroup = subparsers.add_parser(method_name, help=getattr(apiclass, method_name).__doc__)

            # add to the arg cacher
            # arg_parser_cache.add_parser(command, method_name, help=getattr(apiclass, method_name).__doc__)

            # set the callback for the subparser group, using the CallFixer to resolve the callback
            tmpGroup.set_defaults(func=CallProxy(getattr(callback, method_name)))

            # add the default to the cacher
            # arg_parser_cache.add_default(command, apiclass, method_name)
            logger.debug("\tparameters: %s" % inspect.signature(getattr(apiclass, method_name)))

            AutoApi.getArgsForMethod(apiclass, method_name)

            # get the signature of the method
            sig = inspect.signature(getattr(apiclass, method_name))

            # for each parameter, check its type, and add to the subparsers as needed
            for param in sig.parameters.values():
                if param.name != "self" and param.name != "kwargs":

                    # get the type of the param from the doc strings
                    param_type = get_type_param_from_doc_strings(getattr(apiclass, method_name), param)
                    if is_primitive(param_type):
                        logger.debug("adding param: %s type: %s" % (param.name, param_type))
                        tmpGroup.add_argument("--%s" % param, action="store", type=str,
                                              help="type: %s" % param_type)
                    else:
                        logger.debug("ignoring %s because it is a non-primitive" % param_type)
                        tmpGroup.add_argument("--%s" % param, action="store", type=str,
                                              help="file: %s" % param_type)
            # add override values for arbitrary key/value changing of body of yaml for update events
            tmpGroup.add_argument("--override", nargs=2, action="append", type=str,
                                  help="key,val in yaml to override, such as enabled false")

            # check if "where" exists as a param in method's docstring
            x = get_type_param_from_doc_strings(getattr(apiclass, method_name), "where")
            if x:
                tmpGroup.add_argument("--where", nargs=1, action="append", type=str,
                                      help="where filter to apply, e.g: msgVpnName==def*")

            groups.append(tmpGroup)  # this is probably not needed
        logger.debug("created sub-parsers")
        return subparsers
