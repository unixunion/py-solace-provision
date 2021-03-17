import logging

import yaml

from sp.util import to_good_dict
import sp

logger = logging.getLogger('solace-provision')


# this class handles the data types returned by solace
class SolaceResponseProcessor:
    # a place to call with data payloads for example when you want to save to disk
    data_callback = None
    args = None

    def __init__(self, data_callback=None, args=None):
        self.data_callback = data_callback
        self.args = args

    def __call__(self, *args, **kwargs):
        for arg in args:
            logger.debug("arg: %s" % arg)
        logger.debug("kwargs: %s" % kwargs)

        data = args[0]

        if hasattr(data, "data"):
            logger.debug("data present")
            if (isinstance(data.data, list)):
                logger.debug("list response")
                #TODO FIXME list responses dont desserialize into the plural Response object.
                # issue with to_good_dict
                # y = yaml.dump(to_good_dict(data.data))
                # logger.info("response data\n%s" % y)
                # if self.data_callback:
                #     self.data_callback(y, *args, **kwargs)
                data_list = []
                for i in data.data:
                    y = yaml.dump(to_good_dict(i))
                    logger.info("response data\n%s" % y)
                    data_list.append(y)
                if self.data_callback:
                    logger.debug("calling data_callback")
                    try:
                        # try to update completion cache
                        sp.apc.update_choices(data_list, self.args, *args, **kwargs)
                    except Exception as e:
                        pass
                    self.data_callback(data_list, *args, **kwargs)
            else:
                logger.debug("single response")
                y = yaml.dump(to_good_dict(data.data))
                logger.info("response data\n%s" % y)
                if self.data_callback:
                    try:
                        # try to update completion cache
                        sp.apc.update_choices(y, self.args, *args, **kwargs)
                    except Exception as e:
                        pass
                    self.data_callback(y, *args, **kwargs)

        if hasattr(data, "meta"):
            logger.debug("meta is present")
            if data.meta.response_code != 200:
                logger.info("response_code: %s" % data.meta.response_code)
