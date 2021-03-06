import argparse
import logging
import re
import textwrap
from typing import Callable
import inspect

import six
import yaml

import sp

settings = sp.settings

logger = logging.getLogger('solace-provision')

primitive = ("int", "str", "bool")


def load_class(klassname):
    try:
        __import__(klassname, globals())
    except Exception as e:
        logging.error("Failed to import class %s" % klassname)
        raise


def make_kwargs_from_args(args):
    kw = {}
    for k in vars(args):
        if vars(args)[k]:
            logger.debug("adding kwarg: %s:%s" % (k, vars(args)[k]))
            kw[k] = vars(args)[k]
    return kw


def get_client(subcommand=None, config_class=None, client_class=None, **kwargs):
    """
    Creates a client of the type for the passed parameters.

    :param subcommand: the name of the subcommand is used to load the appropriate config sub-attributes under SOLACE_CONFIG
    :param config_class: Class of the config to instantiate
    :param client_class: Class of the client to instantiate
    :return: the client instantiated using the client_class param
    :rtype: object
    """
    config = config_class()

    config.host = settings.solace_config[subcommand]["host"]
    logger.debug("host: %s" % config.host)
    config.username = settings.solace_config[subcommand]["username"]
    config.password = settings.solace_config[subcommand]["password"]
    if "proxy" in settings.solace_config:
        config.proxy = settings.solace_config["proxy"]
    if "ssl" in settings.solace_config:
        if "verify_ssl" in settings.solace_config["ssl"]:
            config.verify_ssl = settings.solace_config["ssl"]["verify_ssl"]
            logger.debug("verify_ssl is %s" % config.verify_ssl)
        if "cert" in settings.solace_config["ssl"]:
            config.ssl_ca_cert = settings.solace_config["ssl"]["cert"]
            logger.debug("cert is %s" % config.ssl_ca_cert)

    for k in kwargs:
        if k != "password":
            logger.info("overriding %s with value %s" % (k, kwargs[k]))
        if k == "host":
            config.host = kwargs[k]
        elif k == "username":
            config.username = kwargs[k]
        elif k == "password":
            config.password = kwargs[k]
        else:
            logger.debug("unknown kwarg: %s" % k)

    try:
        config.host = "%s%s" % (config.host, settings.commands[subcommand]["api_path"])
    except KeyError as e:
        logger.warning("configuration error")
        logger.warning(sp.example_config)

    client = client_class(configuration=config)

    return client


def generic_output_processor(target_method, *args, callback=None, **kwargs):
    logger.debug("genericOutputProcessor calling target with args: %s kwargs: %s" % (args, kwargs))
    data = target_method(*args, **kwargs)
    logger.debug("data: %s" % data)
    if callback:
        callback(data, *args, **kwargs)

    cursor = get_cursor(data)
    if cursor:
        logger.debug("cursor is present")
        kwargs['cursor'] = cursor
        generic_output_processor(target_method, *args, callback=callback, **kwargs)

    return data


# process output, and recurs if cursor is in response
# todo fixme this should not make assumptions about the data type
def process_output(target_method, args, callback=None, **kwargs):
    data = target_method(args, **kwargs)

    logger.debug("data: %s" % data)
    # logger.debug("no data, could be semp meta only")

    if (isinstance(data.data, list)):
        logger.debug("list response")
        for i in data.data:
            logger.info("response data\n%s" % yaml.dump(to_good_dict(i)))
            if callback:
                callback(yaml.dump(to_good_dict(i)))

    else:
        logger.debug("single response")
        logger.info("response data\n%s" % yaml.dump(to_good_dict(data.data)))
        if callback:
            callback(yaml.dump(to_good_dict(data.data)))

    cursor = get_cursor(data)
    if cursor:
        logger.debug("cursor is present")
        process_output(target_method, args, cursor=cursor, callback=callback)

    return data


# simple comparator for simple types
def is_primitive(thing):
    return thing in primitive


# for paginated requests
def get_cursor(data):
    try:
        if data.meta.paging.cursor_query != "":
            return data.meta.paging.cursor_query
    except Exception as e:
        return None


def get_next_page_uri(data):
    try:
        if data.meta.paging.next_page_uri != "":
            return data.meta.paging.next_page_uri
    except Exception as e:
        return None


# re-write keys using the attribute_map
def dict_remap_attr(o, klass):
    result = {}
    for k, v in six.iteritems(o):
        for key, value in klass.attribute_map.items():
            if value == k:
                logger.debug("key %s -> %s" % (k, key))
                result[key] = v
    return result


# fixes the naming of keys when serializing
def to_good_dict(o):
    """Returns the model properties as a dict with correct object names"""

    def val_to_dict(val):
        if hasattr(val, "to_dict"):
            return to_good_dict(val)
        elif isinstance(val, list):
            return list(map(
                lambda x: to_good_dict(x) if hasattr(x, "to_dict") else x,
                val
            ))
        else:
            return val

    result = {}
    o_map = o.attribute_map

    for attr, _ in six.iteritems(o.swagger_types):
        value = getattr(o, attr)
        if isinstance(value, list):
            result[o_map[attr]] = list(map(
                lambda x: to_good_dict(x) if hasattr(x, "to_dict") else x,
                value
            ))
        elif hasattr(value, "to_dict"):
            result[o_map[attr]] = to_good_dict(value)
        elif isinstance(value, dict):
            result[o_map[attr]] = dict(map(
                lambda item: (item[0], val_to_dict(item[1])),
                value.items()
            ))
        else:
            result[o_map[attr]] = value

    return result


# a formatter to keep docstrings in original format for --help cmdline
class PreserveWhiteSpaceWrapRawTextHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __add_whitespace(self, idx, iWSpace, text):
        if idx == 0:
            return text
        return (" " * iWSpace) + text

    def _split_lines(self, text, width):
        textRows = text.splitlines()
        for idx, line in enumerate(textRows):
            search = re.search('\s*[0-9\-]{0,}\.?\s*', line)
            if line.strip() == "":
                textRows[idx] = " "
            elif search:
                lWSpace = search.end()
                lines = [self.__add_whitespace(i, lWSpace, x) for i, x in enumerate(textwrap.wrap(line, width))]
                textRows[idx] = lines
        return [item for sublist in textRows for item in sublist]


# get the type from parameters in docstrings
def get_type_param_from_doc_strings(method, parameterName):
    if hasattr(method, "__doc__"):
        try:
            type_name = re.search(':param (.+?) %s' % parameterName, method.__doc__)
            if type_name:
                logger.debug("get_type_param_from_doc_strings %s: %s" % (parameterName, type_name.group(1)))
                return type_name.group(1)
        except Exception as e:
            return None


def get_type_params_from_doc_strings(method):
    if hasattr(method, "__doc__"):
        try:
            type_name = re.findall('param (.+?) (.+?):', method.__doc__)
            logger.debug(type_name)
            return type_name
        except Exception as e:
            return []


def get_return_type_for_method_docs_strings(method):
    if hasattr(method, "__doc__"):
        try:
            type_name = re.search(':return: (\w+?)\n', method.__doc__)
            logger.debug(type_name)
            return type_name.group(1)
        except Exception as e:
            return None


def str2bool(v):
    return v.lower() in "true"


def get_methods_in_api(apiclass):
    object_methods = [method_name for method_name in dir(apiclass)
                      if callable(getattr(apiclass, method_name)) and not method_name.startswith(
            "__") and not method_name.endswith("with_http_info")]
    logger.debug("got methods: %s" % object_methods)
    return object_methods


def get_methods_args(method: Callable):
    if callable(method):
        try:
            sig = inspect.signature(method)

            params = []
            # for each parameter, check its type, and add to the subparsers as needed
            for param in sig.parameters.values():
                if param.name != "self" and param.name != "kwargs":
                    params.append(param)

            return params
        except Exception as e:
            raise ("Unable to get method args for method: %s" % method)
    else:
        raise ("Method %s is not callable" % method)


def get_method_arg_and_type(method: Callable):
    if callable(method):
        ret = []
        args = get_methods_args(method)
        arg_types = get_type_params_from_doc_strings(method)
        for arg in args:
            logger.debug("checking arg: %s" % arg)
            for tpl in arg_types:
                logger.debug("checking tpl: %s %s" % tpl)
                logger.debug("'%s' == '%s'" % (tpl[1], arg.name))
                logger.debug("%s == %s" % (type(tpl[1]), type(arg.name)))
                if tpl[1] == arg.name:
                    logger.debug("appending")
                    ret.append(tpl)
        return ret
    else:
        raise ("Method %s is not callable" % method)