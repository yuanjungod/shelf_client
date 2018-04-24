import time
import threading
import Queue
import sqlite3
from lib.tools.video_tool import VideoTool
from lib.tools.aliyun import Aliyun
from gateway_proto import device_gateway_pb2
from google.protobuf import any_pb2
import logging


class Camera(object):

    def __init__(self, door, light, aliyun, shelf_current_info, client_config, camera_count=1):
        self.working = 0
        self._light = light
        self._door = door
        self._camera_count = camera_count
        self._aliyun = aliyun
        self.shelf_current_info = shelf_current_info
        self.client_config = client_config
        self._camera_instatnce_list = list()
        self._image_remote_save_url = list()
        for i in range(self._camera_count):
            self._camera_instatnce_list.append(VideoTool.convert_video_2_frame(i))
        self.return_cmd_queue = Queue.Queue()
        self._image_task_queue = Queue.Queue()
        th = threading.Thread(target=self.internal_frame_thread)
        th.start()

    def set_image_remote_save_url(self, image_remote_save_url):
        self._image_remote_save_url = image_remote_save_url

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
            self.working = 0
            request = self._image_task_queue.get()
            self.working = 1
            if request == "shelf_init":
                frame_list = list()
                for frame in self.take_photos():
                    frame_list.append(frame)
                    print(frame.shape)
                self._aliyun.check_account()
                # print ["%s/test/%s.jpg" % ("123", i) for i in range(len(frame_list))]
                print "*************************", self._aliyun.account_info.oss_path
                self._aliyun.push_batch_image_2_aliyun([
                    "%s/test/%s.jpg" % (self._aliyun.account_info.oss_path, i) for i in range(len(frame_list))], frame_list)

                any = any_pb2.Any()
                any.Pack(device_gateway_pb2.MessageSenseData(
                            door_locked=1, images=[device_gateway_pb2.Image(
                                aliyun_oss="%s/test/%s.jpg" % (self._aliyun.account_info.oss_path, i)) for i in range(len(frame_list))]))
                sense_data = device_gateway_pb2.StreamMessage(id=str(time.time()), payload=any)
                logging.debug(sense_data)
                self.return_cmd_queue.put(sense_data)
                logging.debug("init finish")
            else:
                door_status = self._door.get_door_status()
                while door_status.next():
                    frame_list = list()
                    for frame in self.take_photos():
                        frame_list.append(frame)
                        # print(frame.shape)

                    self._aliyun.check_account()
                    self._aliyun.push_batch_image_2_aliyun([
                        "%s/test/%s.jpg" % (self._aliyun.account_info["oss_path"], i) for i in range(len(frame_list))],
                        frame_list)
                    any = any_pb2.Any()
                    any.Pack(device_gateway_pb2.MessageSenseData(
                        device_token=self.client_config["device_token"],
                        door_locked=0, images=[device_gateway_pb2.Image(
                            aliyun_oss="%s/%s-%s/%s.jpg" % (
                                self._aliyun.account_info.oss_path, self.client_config["device_token"], time.time(), i))
                            for i in range(len(frame_list))]))
                    self.return_cmd_queue.put(
                        device_gateway_pb2.StreamMessage(
                            reply_to=request.id,
                            payload=any))

                frame_list = list()
                for frame in self.take_photos():
                    frame_list.append(frame)
                    # print(frame.shape)

                self._aliyun.check_account()
                self._aliyun.push_batch_image_2_aliyun([
                    "%s/test/%s.jpg" % (self._aliyun.account_info.oss_path, i) for i in range(len(frame_list))], frame_list)
                any = any_pb2.Any()
                any.Pack(device_gateway_pb2.MessageSenseData(
                    device_token=self.client_config["device_token"],
                    door_locked=1, images=[device_gateway_pb2.Image(
                        aliyun_oss="%s/test/%s.jpg" % (self._aliyun.account_info.oss_path, i)) for i in range(len(frame_list))]))
                self.return_cmd_queue.put(
                    device_gateway_pb2.StreamMessage(
                        reply_to=request.id,
                        payload=any))

    def push_frames_to_server(self, request):
        self._image_task_queue.put(request)

