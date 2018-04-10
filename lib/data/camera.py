import time
import threading
import Queue
import sqlite3
from lib.tools.video_tool import VideoTool
from example import device_gateway_pb2


class Camera(object):

    def __init__(self, door, queue, light, camera_count=1):
        self.working = 0
        self._light = light
        self._door = door
        self._camera_count = camera_count
        self._camera_instatnce_list = list()
        for i in range(self._camera_count):
            self._camera_instatnce_list.append(VideoTool.convert_video_2_frame(i))
        self._return_cmd_queue = queue
        self._image_task_queue = Queue.Queue()
        th = threading.Thread(target=self.internal_frame_thread)
        th.start()

    def take_photos(self):
        if self._light.get_light_status():
            for i in self._camera_instatnce_list:
                try:
                    yield i.next()
                except:
                    yield None
        else:
            self._light.open_light()
            for i in self._camera_instatnce_list:
                try:
                    i.next()
                except:
                    pass
            for i in self._camera_instatnce_list:
                try:
                    yield i.next()
                except:
                    yield None

    def get_camera_status(self):
        status = True
        for i in self._camera_instatnce_list:
            try:
                i.next()
            except:
                status = False
        return status

    def internal_frame_thread(self):
        while True:
            cmd = self._image_task_queue.get()
            door_status = self._door.get_door_status()
            while door_status.next():
                for frame in self.take_photos():
                    time.sleep(1)
                    print(frame.shape)
                self._return_cmd_queue.put(device_gateway_pb2.CommandResponse(id="1", success=1, door_status=1))
            self._return_cmd_queue.put(device_gateway_pb2.CommandResponse(id="1", success=1, door_status=2))

    def push_frames_to_server(self, cmd):
        self._image_task_queue.put(cmd)

