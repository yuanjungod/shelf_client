from camera import Camera
from door import Door
from light import Light
from example import device_gateway_pb2
import os


class Shelf(object):

    def __init__(self, queue):
        self.is_init = False
        self.in_use = False
        self._camera = None
        self._door = None
        self._light = None
        self._queue = queue

    def init(self):

        self._door = Door()
        self._light = Light()
        self._camera = Camera(self._door, self._queue, self._light)
        self.is_init = True

    def check_device(self):
        if self.is_init is False or self.in_use is True:
            return False
        return True

    def get_device_status(self):
        return True

    def execute_server_command(self, cmd):
        if not self.check_device():
            print "#############################fuck#############################", self.is_init, self.in_use
            return device_gateway_pb2.CommandResponse(ReplyId=cmd.id, time=cmd.time, shelf_id=502, success=2)
        else:
            self.in_use = True
            print("in use")
            self._camera.push_frames_to_server(cmd)
            return device_gateway_pb2.CommandResponse(ReplyId=cmd.id, time=cmd.time, shelf_id=502, success=1)






