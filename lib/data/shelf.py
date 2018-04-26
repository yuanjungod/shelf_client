from camera import Camera
from door import Door
from light import Light
from lock import Lock
from gateway_proto import device_gateway_pb2
from monitor import Monitor
from lib.tools.aliyun import Aliyun
from google.protobuf import any_pb2
import time
import logging
import json
import threading
import random


class Shelf(object):

    def __init__(self, queue, client_config):
        self.is_init = False
        self.in_use = False
        self.can_serve = False
        self.camera = None
        self.door = None
        self.light = None
        self.monitor = None
        self.lock = None
        self._queue = queue
        self._shelf_id = None
        self.aliyun = None
        self.shelf_current_info = None
        self.client_config = client_config
        self.scan_start = -1

    def init(self):
        self.door = Door()
        self.light = Light()
        self.lock = Lock()

        self.monitor = Monitor("localhost", 9999)
        # self.monitor.init()
        self.aliyun = Aliyun(self._queue)
        self.camera = Camera(self.door, self.light, self.aliyun, self.shelf_current_info, self.client_config)
        self._queue.put("shelf_init")
        self.is_init = True

    def check_device(self):
        if self.is_init is True and self.in_use is False and self.camera.working == 0:
            return True
        return False

    def shelf_display(self, message):
        self.monitor.show(message)

    def process_request(self, request):
        if isinstance(request, device_gateway_pb2.StreamMessage):
            logging.info("process_request: %s" % request.payload.type_url)
        else:
            logging.info("process_request: %s" % type(request))
        if request == "shelf_init":
            if self.in_use is False:
                self.in_use = True
                self.camera.push_frames_to_server(request)
        elif isinstance(request, device_gateway_pb2.AuthorizationRequest):
            logging.debug("AuthorizationRequest")
            self._queue.put(request)
        elif request.payload.type_url.find("MessageUnlockDoor") != -1:
            logging.debug("MessageUnlockDoor")
            if request.id != "":
                self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))
            if self.check_device():
                open_result = self.lock.open_lock()
                if open_result:
                    if request.id != "":
                        any = any_pb2.Any()
                        any.Pack(device_gateway_pb2.MessageDeviceState(lock=3))
                        self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))
                else:
                    self.in_use = True
                    logging.debug("in use")
                    try_count = 5
                    while not self.door.is_open() and try_count > 0:
                        try_count -= 1
                        time.sleep(1)

                    if self.door.is_open():
                        self.shelf_display([3, {"open": 1}])
                        self.camera.push_frames_to_server(request)
                    else:
                        self.lock.close_lock()
                        any = any_pb2.Any()
                        any.Pack(device_gateway_pb2.MessageDeviceState(lock=2))
                        self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id, payload=any))
            logging.debug("#############################fuck#############################%s, %s" % (self.is_init, self.in_use))

        elif request.payload.type_url.find("MessageRefreshCode") != -1:
            logging.debug("MessageRefreshCode")
            if request.id != "":
                self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))
            self._queue.put(device_gateway_pb2.AuthorizationRequest())
        elif request.payload.type_url.find("MessageCreateDeviceToken") != -1:
            logging.debug("MessageCreateDeviceToken&*********************************: %s" % request)
            message_code_used = device_gateway_pb2.MessageCreateDeviceToken()
            request.payload.Unpack(message_code_used)
            self.client_config["device_token"] = message_code_used.device_token
            with open("config.json", "w") as f:
                json.dump(self.client_config, f)
            self.shelf_display([
                4, {"device_token": message_code_used.device_token, "biz_name": message_code_used.biz_name}])
            self.scan_start = time.time()
            if request.id != "":
                self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))
        elif request.payload.type_url.find("MessageRevokeDeviceToken") != -1:
            logging.debug("MessageRevokeDeviceToken")
            if request.id != "":
                self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))
            self._queue.put(device_gateway_pb2.AuthorizationRequest())












