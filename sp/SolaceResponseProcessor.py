import logging

import yaml

from sp.util import to_good_dict

logger = logging.getLogger('solace-provision')


# this class handles the data types returned by solace
class SolaceResponseProcessor:
    # a place to call with data payloads for example when you want to save to disk
    data_callback = None

    def __init__(self, data_callback=None):
        self.data_callback = data_callback

    def __call__(self, *args, **kwargs):
        for arg in args:
            logger.debug("arg: %s" % arg)
        logger.debug("kwargs: %s" % kwargs)

        data = args[0]

        if hasattr(data, "data"):
            logger.debug("data present")
            if (isinstance(data.data, list)):
                logger.debug("list response")
                for i in data.data:
                    y = yaml.dump(to_good_dict(i))
                    logger.info("response data\n%s" % y)
                    if self.data_callback:
                        self.data_callback(y, *args, **kwargs)
            else:
                logger.debug("single response")
                y = yaml.dump(to_good_dict(data.data))
                logger.info("response data\n%s" % y)
                if self.data_callback:
                    self.data_callback(y, *args, **kwargs)

        if hasattr(data, "meta"):
            logger.debug("meta is present")
            logger.info("response_code: %s" % data.meta.response_code)
