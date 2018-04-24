#! /usr/bin/env python
# -*- coding: utf-8 -*-
import grpc
import Queue
import os
import json
import uuid
import logging
import logging.config
import time
import traceback
import math
from gateway_proto import device_gateway_pb2, device_gateway_pb2_grpc
from lib.data.shelf import Shelf
from lib.tools.message_controller import MessageController
from lib.interceptors.headers import header_manipulator_client_interceptor


class Client(object):

    Channel = None
    Host = None
    Port = None

    def __init__(self):
        self._config = None
        self._queue = None
        self._shelf = None
        self._message_manage = None
        self.device_id_header = None
        self.device_key_head = None
        self.device_secret_head = None
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S', filemode='a')

    def set_host(cls, host, port):
        cls.Host = host
        cls.Port = port

    def init_channel(cls):
        cls.Channel = grpc.insecure_channel('%s:%s' % (cls.Host, cls.Port))

    def init(self):
        self.init_channel()
        if not os.path.exists("config.json"):
            self._config = dict()
            self._config["uuid"] = uuid.uuid1().get_hex()
            self.device_id_header = header_manipulator_client_interceptor.header_adder_interceptor(
                    "device-id", self._config["uuid"])
            authent_channel = grpc.intercept_channel(self.Channel, self.device_id_header)
            stub = device_gateway_pb2_grpc.DeviceGatewayStub(authent_channel)

            authentication = stub.Authentication(device_gateway_pb2.AuthenticationRequest())
            print authentication
            self._config["device-key"] = authentication.device_key
            self._config["device-secret"] = authentication.device_secret

            self.device_key_head = header_manipulator_client_interceptor.header_adder_interceptor(
                "device-key", self._config["device-key"])

            self.device_secret_head = header_manipulator_client_interceptor.header_adder_interceptor(
                "device-secret", self._config["device-secret"])

            self._config["device_token"] = authentication.device_token
            with open("config.json", "w") as f:
                json.dump(self._config, f)
        else:
            with open("config.json", "r") as f:
                self._config = json.load(f)
            self.device_id_header = header_manipulator_client_interceptor.header_adder_interceptor(
                "device-id", self._config["uuid"])
            self.device_key_head = header_manipulator_client_interceptor.header_adder_interceptor(
                "device-key", self._config["device-key"])
            self.device_secret_head = header_manipulator_client_interceptor.header_adder_interceptor(
                "device-secret", self._config["device-secret"])
            stream_channel = grpc.intercept_channel(self.Channel, self.device_id_header, self.device_key_head, self.device_secret_head)
            stub = device_gateway_pb2_grpc.DeviceGatewayStub(stream_channel)

            authentication = stub.Authentication(device_gateway_pb2.AuthenticationRequest())
            print authentication
            self._config["device-key"] = authentication.device_key
            self._config["device-secret"] = authentication.device_secret

            self.device_key_head = header_manipulator_client_interceptor.header_adder_interceptor(
                "device-key", self._config["device-key"])

            self.device_secret_head = header_manipulator_client_interceptor.header_adder_interceptor(
                "device-secret", self._config["device-secret"])

            self._config["device_token"] = authentication.device_token
            with open("config.json", "w") as f:
                json.dump(self._config, f)

        stream_channel = grpc.intercept_channel(
            self.Channel, self.device_id_header, self.device_key_head, self.device_secret_head)
        self._queue = Queue.Queue()
        self._shelf = Shelf(self._queue, self._config)
        self._message_manage = MessageController(stream_channel, self._shelf, self._queue, self._config)
        self._shelf.init()

    def run(self):
        self.init()
        self._message_manage.run()


if __name__ == "__main__":

    while True:
        count = 1
        try:
            client = Client()
            client.set_host("10.12.2.250", "10000")
            # client.set_host("localhost", "10000")
            client.run()
        except grpc.RpcError:
            print "except"
            logging.error(traceback.format_exc())
            time.sleep(math.pow(2, count))
            count += 1







