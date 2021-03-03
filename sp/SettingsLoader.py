# import logging
# import os
#
# import yaml
#
# logger = logging.getLogger("solace-provision")
#
# primary_config = 'solace.yaml',
#
# try:
#     primary_config = os.environ['PYSOLPRO_CONFIG']
# except Exception as e:
#     pass
#
# __yamlfiles__ = [
#     "%s" % primary_config,
#     "/solace.yaml",
#     '/etc/pysolpro/solace.yaml',
#     '/opt/pysolpro/solace.yaml'
# ]
# __doc__ = """
# The settingsloader searches for a solace.yaml file in above locations.
#
# The environment variable: :envvar:`PYSOLPRO_CONFIG` can also be used to specify another file. e.g
#
#     PYSOLPRO_CONFIG="/tmp/my.yaml" ./pysolpro.py ....
#
# Examples:
#
#     >>> import sp.SettingsLoader as settings
#     >>> settings.CMDB_URL
#     'http://mydomain.com/path'
#
# """
#
# yaml_loaded = False
#
# # defaults which are set / could not be present
# defaults = {
#     "UPDATE_MOCK_TESTS": False,
#     "CMDB_URL": "http://someurl/site.xml",
#     "CMDB_FILE": "provision-example.yaml",
#     "CMDB_USER": "",
#     "CMDB_PASS": "",
#     "SOLACE_QUEUE_PLUGIN": "SolaceQueue"
# }
#
# for yaml_file in __yamlfiles__:
#     if not os.path.exists(yaml_file):
#         continue
#
#     logger.info("Using yaml file %s" % yaml_file)
#     stream = open(yaml_file, 'r')
#     yaml_settings = yaml.safe_load(stream)
#
#     # set the defaults
#     for default in defaults:
#         logging.debug("Setting default %s:%s" % (default, defaults[default]))
#         globals()[default] = defaults[default]
#
#     # TODO FIXME
#     # get each plugins "default" variables and add to globals
#
#     # get the real values if any
#     for variable in yaml_settings.keys():
#         logging.debug("Setting config %s:%s" % (variable, yaml_settings[variable]))
#         globals()[variable] = yaml_settings[variable]
#
#     yaml_loaded = True
#     logging.debug("Yaml loaded successful")
#
#     # logging.info("Loading plugins...")
#     # for p in globals()['PLUGINS']:
#     #     try:
#     #         __import__(p, globals())
#     #     except Exception as e:
#     #         logging.error("Failed to import plugin %s" % p)
#     #         raise
#     # break
#
# if yaml_loaded is False:
#     msg = "Failed to find solace.yaml in any of these locations: %s" % ",".join(__yamlfiles__)
#     logging.error(msg)
#     raise Exception(msg)
