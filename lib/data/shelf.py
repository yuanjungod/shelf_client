from camera import Camera
from device import Device
from light import Light
# from lock import Lock
from lib import device_gateway_pb2
from monitor import Monitor
from lib.tools.aliyun import Aliyun
from lib import any_pb2
import time
import logging
import json


class Shelf(object):

    def __init__(self, queue, client_config, online=True):
        self.is_init = False
        self.in_use = False
        self.can_serve = False
        self.camera = None
        self.device = None
        self.light = None
        self.monitor = None
        self.lock = None
        self._queue = queue
        self._shelf_id = None
        self.aliyun = None
        self.shelf_current_info = None
        self.client_config = client_config
        self.online = online
        self.scan_start = -1

    def init(self):
        self.device = Device()
        self.light = Light()
        # self.lock = Lock()

        self.monitor = Monitor("localhost", 9999)
        # self.monitor.init()
        self.aliyun = Aliyun(self._queue)
        self.camera = Camera(self.device, self.light, self.aliyun, self.shelf_current_info, self.client_config, self.online)
        self._queue.put("shelf_init")
        self.is_init = True

    def check_device(self):
        if self.is_init is True and self.in_use is False and self.camera.working == 0:
            return True
        return False

    def shelf_display(self, message):
        self.monitor.show(message)

    def process_request(self, request):

        if str(type(request)).find("StreamMessage") != -1:
            logging.info("process_request: %s" % request.payload.type_url)
            if request.payload.type_url.find("MessageUnlockDoor") != -1:
                logging.debug("MessageUnlockDoor")
                if request.id != "":
                    self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))
                logging.debug("check device")
                # if self.check_device():

                self.light.open_all_light()
                open_result = self.device.open_lock()
                logging.debug("open lock: %s" % open_result)
                if not open_result:
                    if request.id != "":
                        any = any_pb2.Any()
                        any.Pack(device_gateway_pb2.MessageDeviceState(lock=3))
                        self._queue.put(device_gateway_pb2.StreamMessage(id=str(time.time()), payload=any))
                else:
                    self.in_use = True
                    logging.debug("################in use################")
                    try_count = 5
                    door_status = self.device.door_status.next()
                    while not door_status and try_count > 0:
                        door_status = self.device.door_status.next()
                        try_count -= 1
                        time.sleep(1)

                    if door_status:
                        self.shelf_display([3, {"open": 1}])
                        self.camera.push_frames_to_server(request)
                    else:
                        self.device.lock_lock()
                        any = any_pb2.Any()
                        any.Pack(device_gateway_pb2.MessageDoorClosed())
                        self._queue.put(device_gateway_pb2.StreamMessage(id=str(time.time()), payload=any))
                logging.debug(
                    "#############################fuck#############################%s, %s" % (self.is_init, self.in_use))

            elif request.payload.type_url.find("MessageRefreshCode") != -1:
                logging.debug("MessageRefreshCode")
                if request.id != "":
                    self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))
                self._queue.put(device_gateway_pb2.AuthorizationRequest())
            elif request.payload.type_url.find("MessageCreateDeviceToken") != -1:
                logging.debug("MessageCreateDeviceToken&*********************************: %s" % request)
                message_code_used = device_gateway_pb2.MessageCreateDeviceToken()
                request.payload.Unpack(message_code_used)
                if message_code_used.biz_name == "bind-device":
                    pass
                else:
                    self.client_config["device_token"] = message_code_used.device_token
                    with open("config.json", "w") as f:
                        json.dump(self.client_config, f)
                    self.shelf_display([
                        4, {"device_token": message_code_used.device_token, "biz_name": message_code_used.biz_name}])
                    if self.in_use is False and self.is_init is True:
                        self.in_use = True
                        self.shelf_display([3, {"open": 1}])
                        self.light.open_all_light()
                        self.camera.push_frames_to_server(request)
                        # self.in_use = True

                    self.scan_start = time.time()
                    if request.id != "":
                        self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))
            elif request.payload.type_url.find("MessageRevokeDeviceToken") != -1:
                self.in_use = False
                logging.debug("MessageRevokeDeviceToken")
                if request.id != "":
                    self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))
                logging.debug(type(device_gateway_pb2.AuthorizationRequest()))
                self._queue.put(device_gateway_pb2.AuthorizationRequest())
            else:
                logging.info("process_request: %s" % request)
        elif request == "shelf_init":
            if self.in_use is False:
                self.light.open_all_light()
                self.camera.push_frames_to_server(request)
        elif str(type(request)).find("AuthorizationRequest") != -1:
            logging.debug("AuthorizationRequest")
            self._queue.put(request)
        else:
            logging.info("process_request: %s" % type(request))













