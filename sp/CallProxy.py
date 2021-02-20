# a call wrapper to basically have place to hook in some changes to args on the fly
import argparse
import logging

import yaml

from sp.util import getTypeParamFromDocStrings, is_primitive, str2bool

logger = logging.getLogger('solace-provision')


# proxy the call and correct the args to be *args instead of key=val
class CallProxy(object):
    target = None
    api_instance = None

    def __init__(self, target):
        self.target = target

    def __call__(self, *args, **kwargs):
        logger.debug("called for target %s, args: %s kwargs: %s" % (self.target, args, kwargs))
        new_args = self.resolveArgs(self.target, args)
        if "cursor" in kwargs:
            logger.debug("cursor: %s" % kwargs.get("cursor"))
            return self.target.__call__(*new_args, cursor=kwargs.get("cursor"))
        else:
            logger.debug("no cursor call")
            return self.target.__call__(*new_args)

    def getInstance(self):
        return self.api_instance

    # turns the kwargs from the argparser namespace into plain args, also reads in files for non-primative types
    def resolveArgs(self, method, args: argparse.Namespace):
        logger.debug("resolving args %s" % args)

        function_args = []
        file = None

        for a in args:
            logger.debug("a: %s", a)
            for k, v in a._get_kwargs():
                if not isinstance(v, CallProxy) and k != "override" and v is not None:
                    logger.debug("key: %s, argument: %s" % (k, v))
                    dt = getTypeParamFromDocStrings(method, k)
                    if is_primitive(dt):
                        logger.debug("adding primitive: %s arg: %s" % (dt, v))
                        function_args.append(v)
                    elif dt is not None:
                        logger.debug("read file for type: %s arg: %s" % (dt, v))
                        with open(v) as f:
                            file = yaml.safe_load(f)
            for k, v in a._get_kwargs():
                if k == "override" and v is not None:
                    logger.info("v: %s" % v)
                    for attrib, value in v:
                        logger.info("overriding a: %s, v: %s" % (attrib, value))
                        #logger.debug("overriding %s %s" % (v[0], v[1]))
                        #logger.debug("file[v0]: %s" % file[v[0]])
                        # convert the value type to whatever is in there,
                        # TODO FIXME this is probably not None / null safe
                        if isinstance(file[attrib], bool):
                            file[attrib] = str2bool(value)
                        else:
                            file[attrib] = value
                        logger.debug("file[%s]: %s" % (attrib, value))


        if file is not None:
            function_args.append(file)

        logger.debug("returning args")
        return function_args
