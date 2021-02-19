import argparse
import logging
import re
import textwrap

import six
import solace_semp_client
import yaml

logger = logging.getLogger('solace-provision')

primitive = ("int", "str", "bool")


def getClient(settings=None):
    config = solace_semp_client.Configuration()

    config.host = settings.SOLACE_CONFIG["host"]
    config.username = settings.SOLACE_CONFIG["username"]
    config.password = settings.SOLACE_CONFIG["password"]

    client = solace_semp_client.ApiClient(configuration=config)
    return client


# process output, and recurs if cursor is in response
def processOutput(target_method, args, **kwargs):
    data = target_method(args, **kwargs)

    if (isinstance(data.data, list)):
        logger.debug("list response")
        for i in data.data:
            logger.info("response data\n%s" % yaml.dump(to_good_dict(i)))

    else:
        logger.debug("single response")
        logger.info("response data\n%s" % yaml.dump(to_good_dict(data.data)))

    cursor = getCursor(data)
    if cursor:
        logger.debug("cursor is present")
        processOutput(target_method, args, cursor=cursor)


# simple comparator for simple types
def is_primitive(thing):
    return thing in primitive


# for paginated requests
def getCursor(data):
    try:
        if data.meta.paging.cursor_query != "":
            return data.meta.paging.cursor_query
    except Exception as e:
        return None


def getNextPageUri(data):
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
def getTypeParamFromDocStrings(method, parameterName):
    if hasattr(method, "__doc__"):
        try:
            type_name = re.search(':param (.+?) %s' % parameterName, method.__doc__)
            if type_name:
                logger.debug("\t%s: %s" % (parameterName, type_name.group(1)))
                return type_name.group(1)
        except Exception as e:
            return None


def str2bool(v):
    return v.lower() in ("true")
