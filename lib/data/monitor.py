# -*- coding: utf-8 -*-
import socket
import json


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
        if self.show_socket is None:
            self.init()
        try:
            self.show_socket.sendall(json.dumps(message))
        except:
            print(message)
            self.show_socket.close()
            self.show_socket = None






