# -*- coding: utf-8 -*-
import socket
import json
import logging


class Monitor(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.show_socket = None

    def init(self):
        self.show_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.show_socket.connect((self.host, self.port))

    def check_monitor_status(self):
        return True

    def show(self, message):
        print message
        logging.info(message)
        self.init()
        self.show_socket.sendall(json.dumps(message))
        self.show_socket.close()







