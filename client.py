#!/usr/bin/env python3

import socket
import sys

import sp.SettingsLoader as settings
from sp.nw import recv_msg

BUFF_SIZE = 4096

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((settings.SERVER["host"], settings.SERVER["port"]))
    s.sendall(' '.join(sys.argv[1:]).encode())

    while True:
        data = recv_msg(s)
        if not data:
            break

        print(data.decode("utf-8"))