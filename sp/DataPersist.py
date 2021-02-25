import importlib
import inspect
import logging

import yaml

from sp.util import get_type_param_from_doc_strings, get_return_type_for_method_docs_trings

logger = logging.getLogger('solace-provision')

# def represent_none(self, _):
#     return self.represent_scalar('tag:yaml.org,2002:null', '')
#     # return self.represent_scalar(None, None)
#
# yaml.add_representer(type(None), represent_none)


class DataPersist:

    def __init__(self):
        pass



    def save_object(self, *args, **kwargs):
        # logger.info(args[0])
        logger.debug("data: %s" % args[0])



        method = args[2].func.get_target()  # The method can be fetched from the CallProxy instance
        models = args[2].func.get_models()
        sig = inspect.signature(method)  # get the signature

        mapped_params = {}

        i = 0
        for param in sig.parameters.values():
            try:
                param_type = get_type_param_from_doc_strings(method, param)
                logger.debug("param: %s, param_type: %s, co: %s" % (param, param_type, args[2].func.get_args()[i]))
                mapped_params[param.name] = args[2].func.get_args()[i]
                i += 1
            except Exception as e:
                pass

        # get method passed kwargs
        # for k in args[2].func.get_kwargs():
        #     logger.info("kwarg: %s" % k)

        # all_param_types = get_type_params_from_doc_strings(method)
        # logger.info("all params: %s" % all_param_types)

        return_type = get_return_type_for_method_docs_trings(method)
        return_type_class = getattr(importlib.import_module(models), return_type)

        if isinstance(args[0], list):
            for d in args[0]:
                logger.info(d)

        logger.info("data: %s" % type(args[0]))
        logger.info("models %s" % models)
        logger.info("return type: %s" % return_type)
        logger.info("return type class: %s" % return_type_class)
        logger.info("data type class: %s" % return_type_class.swagger_types['data'])
        logger.info("mapped_params: %s" % mapped_params)

        if isinstance(args[0], list):
            for item in args[0]:
                item = self.delete_nulls(yaml.safe_load(item))
                logger.info("save item: \n---\n%s" % yaml.dump(item))
        else:
            item = self.delete_nulls(yaml.safe_load(args[0]))
            logger.info("save item: \n---\n%s" % yaml.dump(item))



        # logger.info("data type: %s" % type(yaml.safe_load(args[0])))

        pass

    def delete_nulls(self, o):
        for k, v in dict(o).items():
            if isinstance(v, dict):
                o[k] = self.delete_nulls(v)
            else:
                if v is None:
                    del o[k]
        return o