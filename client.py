#! /usr/bin/env python
# -*- coding: utf-8 -*-
import grpc
import Queue
import threading
import os
import json
import uuid
import time
from gateway_proto import device_gateway_pb2, device_gateway_pb2_grpc
from lib.data.shelf import Shelf
from lib.tools.message_manage import MessageManage


class Client(object):

    def __init__(self, host, port):

        self._host = host
        self._port = port
        self._config = None
        self._channel = grpc.insecure_channel('%s:%s' % (self._host, self._port))

        self._queue = Queue.Queue()
        self._shelf = Shelf(self._queue)
        self._message_manage = MessageManage(
            self._channel, self._shelf, self._queue)
        self._shelf.init()

    def init(self, stub=None):
        if stub is None:
            stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
        if not os.path.exists("config.json"):
            print("1")
            self._config = dict()
            self._config["uuid"] = uuid.uuid1().get_hex()
            authentication = stub.Authentication(device_gateway_pb2.AuthenticationRequest(device_id=self._config["uuid"]))
            print("2")
            self._config["token"] = authentication.token
            self._config["SerialNumber"] = authentication.SerialNumber
            authorization = stub.Authorization(device_gateway_pb2.AuthorizationRequest(token=self._config["token"]))
            self._config["code"] = authorization.code
            self._config["qr_code"] = authorization.qr_code
            self._config["expires_in"] = time.time() + authorization.expires_in
            with open("config.json", "w") as f:
                json.dump(self._config, f)
        else:
            if self._config is None:
                with open("config.json", 'r') as load_f:
                    self._config = json.load(load_f)
            if self._config["expires_in"] < time.time():
                authorization = stub.Authorization(device_gateway_pb2.AuthorizationRequest(token=self._config["token"]))
                self._config["code"] = authorization.code
                self._config["qr_code"] = authorization.qr_code
                self._config["expires_in"] = time.time() + authorization.expires_in
                with open("config.json", "w") as f:
                    json.dump(self._config, f)

    def timed_task(self):
        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
        while True:
            time.sleep(100)
            self.init(stub)

    def run(self):

        self.init()

        timed_task = threading.Thread(target=self.timed_task)
        timed_task.start()

        self._message_manage.run()


if __name__ == "__main__":

    client = Client("localhost", "50051")
    client.run()





