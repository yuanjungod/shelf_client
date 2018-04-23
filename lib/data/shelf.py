from camera import Camera
from door import Door
from light import Light
from lock import Lock
from gateway_proto import device_gateway_pb2
from monitor import Monitor
from lib.tools.aliyun import Aliyun
from google.protobuf import any_pb2
import time


class Shelf(object):

    def __init__(self, queue):
        self.is_init = False
        self.in_use = False
        self.camera = None
        self.door = None
        self.light = None
        self.monitor = None
        self.lock = None
        self._queue = queue
        self._shelf_id = None
        self.aliyun = None
        self.shelf_current_info = dict()

    def init(self):
        self.door = Door()
        self.light = Light()
        self.lock = Lock()

        self.monitor = Monitor("localhost", 9999)
        # self.monitor.init()
        self.aliyun = Aliyun(self._queue)
        self.camera = Camera(self.door, self._queue, self.light, self.aliyun)
        self._queue.put("shelf_init")
        self.is_init = True

    def check_device(self):
        # print self.is_init, self.in_use, self.camera.working
        if self.is_init is True and self.in_use is False and self.camera.working == 0:
            return True
        return False

    def shelf_display(self, message):
        print "shelf_display", message
        self.monitor.show(message)

    def process_request(self, request):

        if request == "shelf_init":
            if self.in_use is False:
                self.in_use = True
                self.camera.push_frames_to_server(request)

        elif request.payload.type_url.find("MessageUnlockDoor") != -1:
            # print "self.check_device()", self.check_device()
            self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))
            if self.check_device():
                open_result = self.lock.open_lock()
                if open_result:
                    return device_gateway_pb2.StreamMessage(reply_to=request.id)
                else:
                    self.in_use = True
                    print("in use")
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
                    any.Pack(device_gateway_pb2.MessageDoorLocked())
                    return device_gateway_pb2.StreamMessage(reply_to=request.id, payload=any)

            print "#############################fuck#############################", self.is_init, self.in_use

        elif request.payload.type_url.find("MessageRefreshCode") != -1:
            # print request
            self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))
            self._queue.put(device_gateway_pb2.AuthorizationRequest())
        elif request.payload.type_url.find("MessageCodeUsed") != -1:
            self.shelf_display([4, {"scan": request.payload.device_token}])
            self._queue.put(device_gateway_pb2.StreamMessage(reply_to=request.id))










