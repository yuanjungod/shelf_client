#! /usr/bin/env python
# -*- coding: utf-8 -*-
import grpc
import Queue
import os
import json
import uuid
from gateway_proto import device_gateway_pb2, device_gateway_pb2_grpc
from lib.data.shelf import Shelf
from lib.tools.message_controller import MessageController
from lib.interceptors.headers import header_manipulator_client_interceptor


class Client(object):

    def __init__(self, host, port):

        self._host = host
        self._port = port
        self._config = None
        self._channel = None
        self._queue = None
        self._shelf = None
        self._message_manage = None

    def init(self, stub=None):
        self._channel = grpc.insecure_channel('%s:%s' % (self._host, self._port))
        if stub is None:
            stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
        if not os.path.exists("config.json"):
            self._config = dict()
            self._config["uuid"] = uuid.uuid1().get_hex()
            authentication = stub.Authentication(device_gateway_pb2.AuthenticationRequest())
            self._config["device_secret"] = authentication.device_secret
            self._config["device_token"] = authentication.device_token
            with open("config.json", "w") as f:
                json.dump(self._config, f)
        else:
            with open("config.json", "r") as f:
                self._config = json.load(f)
        header_adder_interceptor = header_manipulator_client_interceptor.header_adder_interceptor(
            self._config["uuid"], self._config["device_secret"])
        # grpc.intercept_channel(self._channel, header_adder_interceptor)
        self._queue = Queue.Queue()
        self._shelf = Shelf(self._queue)
        self._message_manage = MessageController(self._channel, self._shelf, self._queue)
        self._shelf.init()

    def run(self):
        self.init()
        self._message_manage.run()


if __name__ == "__main__":

    client = Client("localhost", "50051")
    client.run()





