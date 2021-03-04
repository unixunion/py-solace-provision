from libksettings import KSettings

settings = KSettings(config_filename="solace.yaml",
                     config_filename_envvar="PYSOLPRO_CONFIG",
                     PLUGINS=[],
                     config_load_locations=[".", "/", "/opt/pysolpro", "/etc/pysolpro"],
                     load_yaml=True)
