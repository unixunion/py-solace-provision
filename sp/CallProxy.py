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
    args = None
    kwargs = None
    models = None

    def __init__(self, target, models=None):
        self.target = target
        self.models = models

    def __call__(self, *args, **kwargs):
        logger.debug("called for target %s, args: %s kwargs: %s" % (self.target, args, kwargs))
        new_args, new_kwargs = self.resolveArgs(self.target, args)

        where = new_kwargs.get("where")
        if where:
            kwargs["where"] = where

        opaque_password = new_kwargs.get("opaque_password")
        if opaque_password:
            kwargs["opaque_password"] = opaque_password

        self.args = new_args
        self.kwargs = kwargs
        logger.debug("calling method with args: %s and kwargs: %s" % (new_args, kwargs))
        return self.target.__call__(*new_args, **kwargs)

    def get_target(self):
        return self.target

    def get_args(self):
        """
        Get the passed args to the call
        :return:
        """
        return self.args

    def get_kwargs(self):
        """
        Get the passed kwargs to the call
        :return:
        """
        return self.kwargs

    def get_models(self):
        return self.models

    # def getInstance(self):
    #     return self.api_instance

    # turns the kwargs from the argparser namespace into plain args, also reads in files for non-primative types
    def resolveArgs(self, method, args: argparse.Namespace):
        logger.debug("resolving args %s" % args)

        function_args = []
        function_kwargs = {}
        file = None

        for a in args:
            logger.debug("a: %s", a)
            for k, v in a._get_kwargs():
                # ignored args, which are not part of the positional args of a method
                if not isinstance(v, CallProxy) and k != "override" and k != "where" and k != "opaque_password" and k != "password" and  k != "username" and k != "host" and v is not None:
                    logger.debug("key: %s, argument: %s" % (k, v))
                    dt = get_type_param_from_doc_strings(method, k)
                    if is_primitive(dt):
                        logger.debug("adding primitive: %s arg: %s" % (dt, v))
                        function_args.append(v)
                    elif dt is not None:
                        logger.debug("reading file for type: %s arg: %s" % (dt, v))
                        try:
                            with open(v) as f:
                                file = yaml.safe_load(f)
                                if file is None:
                                    logger.debug("empty file, making empty instance")
                                    file = {}
                                logger.debug("read file %s" % file)
                        # older broker
                        except Exception as e:
                            logger.warning("unable to load file: %s" % file)
                            raise
            for k, v in a._get_kwargs():
                if k == "override" and v is not None:
                    logger.debug("v: %s" % v)
                    for attrib, value in v:
                        logger.info("overriding a: %s, v: %s" % (attrib, value))
                        # check if the value in the file is a boolean
                        try:
                            if isinstance(file[attrib], bool):
                                file[attrib] = str2bool(value)
                            else:
                                file[attrib] = value
                            logger.debug("file[%s]: %s" % (attrib, value))
                        except Exception as e:
                            logger.error("unknown attribute, '%s' is not present in file" % attrib)
                            raise
                if k == "where" and v is not None:
                    logger.debug("where v: %s" % v)
                    new_where = []
                    for select in v:
                        new_where.append(select[0])
                    logger.debug("new_where: %s" % new_where)
                    function_kwargs["where"] = new_where

                if k == "opaque_password" and v is not None:
                    function_kwargs["opaque_password"] = v

        if file is not None:
            function_args.append(file)

        logger.debug("returning args")
        return function_args, function_kwargs
