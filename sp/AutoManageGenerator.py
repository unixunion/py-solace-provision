import inspect
import logging

from solace_semp_config import AllApi

from sp.CallProxy import CallProxy
from sp.util import is_primitive, getTypeParamFromDocStrings

logger = logging.getLogger('solace-provision')


# scans the klasses and creates a command line parser for them
class AutoManageGenerator(object):
    __slots__ = []
    name = "vpn"
    help = "vpn help text..."

    klasses = [
        {"api": AllApi}
    ]

    parsers = []

    def __init__(self, parser, api_client):
        if parser:
            for provider_api in self.klasses:
                t = provider_api["api"](api_client=api_client)
                self.parsers.append(self.autoSubCommandArgParser(subparsers=parser,
                                                                 apiclass=provider_api["api"],
                                                                 callback=provider_api["api"](
                                                                     api_client=api_client)))

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
    def autoSubCommandArgParser(self, subparsers=None, apiclass=None, callback=None):
        logger.debug("getting methods")
        object_methods = [method_name for method_name in dir(apiclass)
                          if callable(getattr(apiclass, method_name)) and not method_name.startswith(
                "__") and not method_name.endswith("with_http_info")]
        logger.debug("got methods")

        logger.debug(object_methods)

        # holder for groups
        groups = []

        # inspect.getfullargspec(a_method)
        for method_name in object_methods:
            logger.debug("method: %s " % method_name)

            # create the "method" subparser, sucking the dock strings into the help kwarg
            groups.append(subparsers.add_parser(method_name, help=getattr(apiclass, method_name).__doc__))

            # set the callback for the subparser group, using the CallFixer to resolve the callback
            groups[len(groups) - 1].set_defaults(func=CallProxy(getattr(callback, method_name)))
            logger.debug("\tparameters: %s" % inspect.signature(getattr(apiclass, method_name)))

            AutoManageGenerator.getArgsForMethod(apiclass, method_name)

            # get the signature of the method
            sig = inspect.signature(getattr(apiclass, method_name))

            # for each parameter, check its type, and add to the subparsers as needed
            for param in sig.parameters.values():
                if param.name != "self" and param.name != "kwargs":
                    current_group = groups[len(groups) - 1]
                    param_type = getTypeParamFromDocStrings(getattr(apiclass, method_name), param)
                    if is_primitive(param_type):
                        logger.debug("adding param: %s type: %s" % (param.name, param_type))
                        current_group.add_argument("--%s" % param, action="store", type=str,
                                                   help="type: %s" % param_type)
                    else:
                        logger.debug("ignoring %s because it is a non-primitive" % param_type)
                        # was --file fixed
                        current_group.add_argument("--%s" % param, action="store", type=str,
                                                   help="file: %s" % param_type)
            # add override values for arbitrary key/value changing of body of yaml for update events
            groups[len(groups) - 1].add_argument("--override", nargs=2, action="append", type=str,
                                                 help="key,val in yaml to override, such as enabled false")
        logger.debug("created sub-parsers")
        return subparsers
