#! /usr/bin/env python
# -*- coding: utf-8 -*-
import grpc
import Queue
import threading
import os
import json
import uuid
import time
from example import device_gateway_pb2, device_gateway_pb2_grpc
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

    def init(self, stub):
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

    def process_server_command(self):
        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)

        self.init(stub)
        print "process_server_command"
        # requests = stub.Command(device_gateway_pb2.CommandResponse(id="0"))
        # requests = stub.Command()

        # for request in requests:
        #     self._shelf.get_device_status()

            # self._message_manage.add_request_queue(request)

            # stub.Command(self._shelf.execute_server_command(feature))
            # self.init(stub)

    def process_slow_event_report(self):
        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)

        print "report_local_message"
        while True:
            shelf_info = self._queue.get()
            print "process_event"
            self._shelf.get_device_status()

            stub.Command(shelf_info)
            if shelf_info.door_status == 2:
                self._shelf.in_use = False

    def timed_task(self):
        stub = device_gateway_pb2_grpc.DeviceGatewayStub(self._channel)
        while True:
            time.sleep(5)
            if not self._shelf.get_device_status():
                pass

    def run(self):
        # slow_event_report = threading.Thread(target=self.process_slow_event_report)
        # slow_event_report.start()
        # timed_task = threading.Thread(target=self.timed_task)
        # timed_task.start()
        self.process_server_command()
        self._message_manage.run()


if __name__ == "__main__":

    client = Client("localhost", "50051")
    client.run()





