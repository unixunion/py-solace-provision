#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import argparse
import logging
import socketserver
import sys

from solace_semp_config.rest import ApiException

import sp.settingsloader as settings
from sp.AutoManageGenerator import AutoManageGenerator
from sp.nw import send_msg
from sp.util import PreserveWhiteSpaceWrapRawTextHelpFormatter, processOutput, getClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# list of "plugins" to load
sp_modules = [
    AutoManageGenerator
]

# populated at runtime
active_modules = []


class NetworkCallback:
    sock = None

    def __init__(self, sock):
        self.sock = sock

    def __call__(self, *args, **kwargs):
        logger.info("NC: %s" % args)
        logger.info("NC type: %s", type(args))
        logger.info(args)
        send_msg(self.sock, args[0].encode())


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} request:".format(self.client_address[0]))
        print(self.data)
        self.data = self.data.decode("utf-8")
        args = parser.parse_args(self.data.split())
        try:
            processOutput(args.func, args, callback=NetworkCallback(self.request))  # self.request.sendall
        except ApiException as e:
            logger.error("error occurred %s" % e)
        except AttributeError as e:
            logger.error("attribute error %s" % e)
        except TypeError as e:
            logger.error("type error %s" % e)
        except Exception as e:
            logger.error("exception: %s" % e)


if __name__ == '__main__':
    client = getClient(settings=settings)

    parser = argparse.ArgumentParser(prog='pySolPro', formatter_class=PreserveWhiteSpaceWrapRawTextHelpFormatter, exit_on_error=False)
    def x():
        pass
    parser.__setattr__("exit", x)
    subparsers = parser.add_subparsers(help='sub-command help')
    [active_modules.append(m(subparsers, client)) for m in sp_modules]

    with socketserver.TCPServer((settings.SERVER["host"], settings.SERVER["port"]), MyTCPHandler) as server:
        server.serve_forever()

