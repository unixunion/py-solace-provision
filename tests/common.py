import argparse

import solace_semp_action
import solace_semp_config
import solace_semp_monitor
from solace_semp_action import AllApi as ActionAllApi
from solace_semp_config import AllApi as ConfigAllApi
from solace_semp_monitor import AllApi as MonitorAllApi

from sp.AutoApi import AutoApi
from sp.util import get_client


def bootstrap():
    klasses = [
        {
            "api": ConfigAllApi,
            "models": "solace_semp_config.models",
            "subcommand": "config",
            "config_class": solace_semp_config.Configuration,
            "client_class": solace_semp_config.ApiClient
        },
        {
            "api": MonitorAllApi,
            "models": "solace_semp_monitor.models",
            "subcommand": "monitor",
            "config_class": solace_semp_monitor.Configuration,
            "client_class": solace_semp_monitor.ApiClient
        },
        {
            "api": ActionAllApi,
            "models": "solace_semp_action.models",
            "subcommand": "action",
            "config_class": solace_semp_action.Configuration,
            "client_class": solace_semp_action.ApiClient
        }
    ]
    client = get_client

    parser = argparse.ArgumentParser(prog='pySolPro')
    parser.add_argument("--save", dest="save", action='store_true', default=False,
                             help="save retrieved data to disk")
    parser.add_argument("--save-dir", dest="savedir", action="store", default="savedata",
                             help="location to save to")
    subparsers = parser.add_subparsers(help='sub-command help')
    aa = AutoApi(subparsers, client, klasses=klasses)
    return parser, aa