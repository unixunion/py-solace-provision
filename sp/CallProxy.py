# a call wrapper to basically have place to hook in some changes to args on the fly
import argparse
import logging

import yaml

from sp.util import get_type_param_from_doc_strings, is_primitive, str2bool

logger = logging.getLogger('solace-provision')
logger.debug("imported")


# proxy the call and correct the args to be *args instead of key=val
class CallProxy(object):
    target = None
    api_instance = None

    def __init__(self, target):
        self.target = target

    def __call__(self, *args, **kwargs):
        logger.debug("called for target %s, args: %s kwargs: %s" % (self.target, args, kwargs))
        new_args, new_kwargs = self.resolveArgs(self.target, args)

        cursor = kwargs.get("cursor")
        where = new_kwargs.get("where")

        if cursor and where:
            return self.target.__call__(*new_args, cursor=cursor, where=where)
        elif cursor:
            return self.target.__call__(*new_args, cursor=cursor)
        elif where:
            return self.target.__call__(*new_args, where=where)
        else:
            return self.target.__call__(*new_args)


    def getInstance(self):
        return self.api_instance

    # turns the kwargs from the argparser namespace into plain args, also reads in files for non-primative types
    def resolveArgs(self, method, args: argparse.Namespace):
        logger.debug("resolving args %s" % args)

        function_args = []
        function_kwargs = {}
        file = None

        for a in args:
            logger.debug("a: %s", a)
            for k, v in a._get_kwargs():
                if not isinstance(v, CallProxy) and k != "override" and k != "where" and v is not None:
                    logger.debug("key: %s, argument: %s" % (k, v))
                    dt = get_type_param_from_doc_strings(method, k)
                    if is_primitive(dt):
                        logger.debug("adding primitive: %s arg: %s" % (dt, v))
                        function_args.append(v)
                    elif dt is not None:
                        logger.debug("reading file for type: %s arg: %s" % (dt, v))
                        with open(v) as f:
                            file = yaml.safe_load(f)
                            if file is None:
                                logger.debug("empty file, making empty instance")
                                file = {}
                            logger.debug("read file %s" % file)
            for k, v in a._get_kwargs():
                if k == "override" and v is not None:
                    logger.debug("v: %s" % v)
                    for attrib, value in v:
                        logger.info("overriding a: %s, v: %s" % (attrib, value))
                        # logger.debug("overriding %s %s" % (v[0], v[1]))
                        # logger.debug("file[v0]: %s" % file[v[0]])
                        # convert the value type to whatever is in there,
                        # TODO FIXME this is probably not None / null safe
                        if isinstance(file[attrib], bool):
                            file[attrib] = str2bool(value)
                        else:
                            file[attrib] = value
                        logger.debug("file[%s]: %s" % (attrib, value))
                if k == "where" and v is not None:
                    logger.debug("where v: %s" % v)
                    new_where = []
                    for select in v:
                        new_where.append(select[0])
                    logger.debug("new_where: %s" % new_where)
                    function_kwargs["where"] = new_where

        if file is not None:
            function_args.append(file)

        logger.debug("returning args")
        return function_args, function_kwargs
