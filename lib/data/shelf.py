from camera import Camera
from door import Door
from light import Light
from gateway_proto import device_gateway_pb2
from monitor import Monitor


class Shelf(object):

    def __init__(self, queue):
        self.is_init = False
        self.in_use = False
        self.camera = None
        self.door = None
        self.light = None
        self.monitor = None
        self._queue = queue
        self._shelf_id = None

    def init(self):

        self.door = Door()
        self.light = Light()
        self.camera = Camera(self.door, self._queue, self.light)
        self.monitor = Monitor("localhost", 9002)
        self.is_init = True

    def set_shelf_id(self, shelf_id):
        self._shelf_id = shelf_id

    def check_device(self):
        if self.is_init is False or self.in_use is True:
            return False
        return True

    def get_device_status(self):
        return True

    def shelf_display(self, message):
        self.monitor.show(message)

    def process_request(self, request):
        if not self.check_device():
            print "#############################fuck#############################", self.is_init, self.in_use
            return device_gateway_pb2.CommandResponse(
                ReplyId=request.id, time=request.time, shelf_id=self._shelf_id, success=2)
        else:
            self.in_use = True
            print("in use")
            self.camera.push_frames_to_server(request)
            return device_gateway_pb2.CommandResponse(
                ReplyId=request.id, time=request.time, shelf_id=self._shelf_id, success=1)






