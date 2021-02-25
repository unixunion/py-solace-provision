import importlib
import logging

logger = logging.getLogger('solace-provision')


def create_subcmd_config(cmd, module_name, models_package, api_class, config_class, client_class):
    try:
        logger.info("importing: %s->%s" % (module_name, api_class))
        _api_class = getattr(importlib.import_module(module_name), api_class)
        _config_class = getattr(importlib.import_module(module_name), config_class)
        _client_class = getattr(importlib.import_module(module_name), client_class)

        klasses = {
            "module": module_name,
            "models": models_package,
            "api": _api_class,
            "subcommand": cmd,
            "config_class": _config_class,
            "client_class": _client_class
        }

        return klasses
    except ModuleNotFoundError as e:
        logger.warning("module %s is not available for this version of SEMP API" % module_name)
        return
