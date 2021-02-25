import hashlib
import importlib
import inspect
import logging
import os
import re
from collections import OrderedDict

import yaml

from sp.util import get_type_param_from_doc_strings, get_return_type_for_method_docs_trings

logger = logging.getLogger('solace-provision')


class DataPersist:

    save_data = False
    save_dir = None

    def __init__(self, save_data=False, save_dir="savedata"):
        self.save_data = save_data
        self.save_dir = save_dir


    def __call__(self, *args, **kwargs):
        if self.save_data:

            # logger.info(args[0])
            logger.debug("data: %s" % args[0])

            method = args[2].func.get_target()  # The method can be fetched from the CallProxy instance
            models = args[2].func.get_models()
            sig = inspect.signature(method)  # get the signature

            mapped_params = OrderedDict()

            i = 0
            for param in sig.parameters.values():
                try:
                    param_type = get_type_param_from_doc_strings(method, param)
                    logger.info("param: %s, param_type: %s, co: %s" % (param, param_type, args[2].func.get_args()[i]))
                    mapped_params[param.name] = args[2].func.get_args()[i]
                    i += 1
                except Exception as e:
                    pass


            return_type = get_return_type_for_method_docs_trings(method)
            return_type_class = getattr(importlib.import_module(models), return_type)
            return_data_type = return_type_class.swagger_types['data']

            if isinstance(args[0], list):
                for d in args[0]:
                    logger.info(d)

            # logger.info("data: %s" % type(args[0]))
            # logger.info("models %s" % models)
            # logger.info("return type: %s" % return_type)
            # logger.info("return type class: %s" % return_type_class)
            logger.info("data type class: %s" % return_data_type)
            logger.info("mapped_params: %s" % mapped_params)

            if isinstance(args[0], list):
                ret_type = re.search('list\[(\w+?)\]', return_data_type).group(1)
                path = "%s/%s" % (mapped_params.get("msg_vpn_name"), ret_type)
                for item in args[0]:
                    item = self.delete_nulls(yaml.safe_load(item))
                    logger.info("save item: %s\n---\n%s" % (path, yaml.dump(item)))
                    self.write_object(item, path, "%s.yaml" % hashlib.sha224(yaml.dump(item).encode("UTF-8")).hexdigest())
            else:
                item = self.delete_nulls(yaml.safe_load(args[0]))
                path = "%s/%s" % (mapped_params.get("msg_vpn_name"), return_data_type)
                logger.info("save item: %s\n---\n%s" % (path, yaml.dump(item)))
                self.write_object(item, path, "%s.yaml" % hashlib.sha224(yaml.dump(item).encode("UTF-8")).hexdigest())


    def write_object(self, data, subpath, file_name):
        filepath = "%s/%s/%s" % (self.save_dir, subpath, file_name)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            yaml.dump(data, f, default_flow_style=False)


    def delete_nulls(self, o):
        for k, v in dict(o).items():
            if isinstance(v, dict):
                o[k] = self.delete_nulls(v)
            else:
                if v is None:
                    del o[k]
        return o