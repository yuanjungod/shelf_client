import time
import threading
import Queue
import sqlite3
from lib.tools.video_tool import VideoTool
from lib.tools.aliyun import Aliyun
from lib import device_gateway_pb2
from lib import any_pb2
import logging
import cv2
import os
import datetime


class Camera(object):

    def __init__(self, device, light, aliyun, shelf_current_info, client_config, online=True, camera_count=3):
        self.working = 0
        self._light = light
        self._device = device
        self._camera_count = camera_count
        self._aliyun = aliyun
        self.shelf_current_info = shelf_current_info
        self.client_config = client_config
        self.online = online
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
        if self._light.is_open:
            for i in self._camera_instatnce_list:
                try:
                    yield i.next()
                except:
                    yield None
        else:
            self._light.open_light()
            time.sleep(2)
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
                if self.online:
                    self._aliyun.check_account()
                    # print ["%s/test/%s.jpg" % ("123", i) for i in range(len(frame_list))]
                    print "*************************", self._aliyun.account_info.oss_path
                    self._aliyun.push_batch_image_2_aliyun([
                        "%s/test/%s.jpg" % (self._aliyun.account_info.oss_path, i) for i in range(len(frame_list))], frame_list)

                    any = any_pb2.Any()
                    any.Pack(device_gateway_pb2.MessageSenseData(
                                door_locked=True, images=[device_gateway_pb2.MessageSenseData.Image(
                                    aliyun_oss="%s/test/%s.jpg" % (
                                        self._aliyun.account_info.oss_path, i)) for i in range(len(frame_list))]))
                    sense_data = device_gateway_pb2.StreamMessage(id=str(time.time()), payload=any)
                    # logging.debug(sense_data)
                    self.return_cmd_queue.put(sense_data)
                    logging.debug("init finish")
                else:
                    if not os.path.exists("images"):
                        os.makedirs("images")
                    if not os.path.exists("images/%s" % datetime.date.today()):
                        os.makedirs("images/%s" % datetime.date.today())
                    photo_time = time.time()
                    for i in range(len(frame_list)):
                        cv2.imwrite("images/%s/%s-%s.jpg" % (datetime.date.today(), photo_time, i), frame_list[i])
                    any = any_pb2.Any()
                    any.Pack(device_gateway_pb2.MessageSenseData(
                        door_locked=True, images=[device_gateway_pb2.MessageSenseData.Image(
                            local_path="http://192.168.1.180:8888/images/%s/%s-%s.jpg" % (
                                datetime.date.today(), photo_time, i)) for i in range(len(frame_list))]))
                    sense_data = device_gateway_pb2.StreamMessage(id=str(time.time()), payload=any)
                    logging.debug(sense_data)
                    self.return_cmd_queue.put(sense_data)

            else:
                any = any_pb2.Any()
                any.Pack(device_gateway_pb2.MessageDoorOpened())
                self.return_cmd_queue.put(device_gateway_pb2.StreamMessage(id=str(time.time()), payload=any))
                while self._device.door_status.next():
                    frame_list = list()
                    for frame in self.take_photos():
                        frame_list.append(frame)
                    if self.online:
                        self._aliyun.check_account()
                        photo_time = time.time()
                        self._aliyun.push_batch_image_2_aliyun([
                            "%s/%s-%s/%s.jpg" % (
                                self._aliyun.account_info.oss_path, self.client_config["device_token"], photo_time, i) for i in range(len(frame_list))],
                            frame_list)
                        any = any_pb2.Any()
                        logging.debug("########asjdsakhcajbkcjahjcajscjascaschashlcaskcklaskck")
                        any.Pack(device_gateway_pb2.MessageSenseData(
                            device_token=self.client_config["device_token"],
                            door_locked=False, images=[device_gateway_pb2.MessageSenseData.Image(
                                aliyun_oss="%s/%s-%s/%s.jpg" % (
                                    self._aliyun.account_info.oss_path, self.client_config["device_token"], photo_time, i))
                                for i in range(len(frame_list))]))
                        self.return_cmd_queue.put(device_gateway_pb2.StreamMessage(payload=any))
                    else:
                        photo_time = time.time()
                        if not os.path.exists("images"):
                            os.makedirs("images")
                        if not os.path.exists("images/%s" % datetime.date.today()):
                            os.makedirs("images/%s" % datetime.date.today())
                        for i in range(len(frame_list)):
                            cv2.imwrite("images/%s/%s-%s.jpg" % (datetime.date.today(), photo_time, i), frame_list[i])
                        any = any_pb2.Any()
                        any.Pack(device_gateway_pb2.MessageSenseData(
                            device_token=self.client_config["device_token"],
                            door_locked=False,
                            images=[device_gateway_pb2.MessageSenseData.Image(
                                local_path="http://192.168.1.180:8888/images/%s/%s-%s.jpg" % (
                                    datetime.date.today(), photo_time, i)) for i in range(len(frame_list))]))
                        sense_data = device_gateway_pb2.StreamMessage(id=str(time.time()), payload=any)
                        logging.debug(sense_data)
                        self.return_cmd_queue.put(sense_data)

                try_count = 3
                result = self._device.lock_lock()
                while result is False and try_count > 0:
                    time.sleep(1)
                    result = self._device.lock_lock()
                    try_count -= 1

                logging.debug("sleeping!sleeping!sleeping!sleeping!sleeping!")
                time.sleep(2)

                any = any_pb2.Any()
                any.Pack(device_gateway_pb2.MessageDoorClosed())
                self.return_cmd_queue.put(device_gateway_pb2.StreamMessage(payload=any))

                frame_list = list()
                for frame in self.take_photos():
                    frame_list.append(frame)
                if self.online:
                    photo_time = time.time()
                    self._aliyun.check_account()
                    self._aliyun.push_batch_image_2_aliyun([
                        "%s/%s-%s/%s.jpg" % (
                            self._aliyun.account_info.oss_path, self.client_config["device_token"], photo_time, i)
                        for i in range(len(frame_list))], frame_list)

                    any = any_pb2.Any()
                    any.Pack(device_gateway_pb2.MessageSenseData(
                        device_token=self.client_config["device_token"],
                        door_locked=True, images=[device_gateway_pb2.MessageSenseData.Image(
                            aliyun_oss="%s/%s-%s/%s.jpg" % (
                                self._aliyun.account_info.oss_path, self.client_config["device_token"], photo_time, i))
                            for i in range(len(frame_list))]))
                    self.return_cmd_queue.put(device_gateway_pb2.StreamMessage(id=str(time.time()), payload=any))
                else:
                    logging.debug("door closeing image")
                    photo_time = time.time()
                    for i in range(len(frame_list)):
                        if not os.path.exists("images"):
                            os.makedirs("images")
                        if not os.path.exists("images/%s" % datetime.date.today()):
                            os.makedirs("images/%s" % datetime.date.today())
                        cv2.imwrite("images/%s/%s-%s.jpg" % (datetime.date.today(), photo_time, i), frame_list[i])
                    any = any_pb2.Any()
                    any.Pack(device_gateway_pb2.MessageSenseData(
                        door_locked=True, images=[device_gateway_pb2.MessageSenseData.Image(
                            local_path="http://192.168.1.180:8888/images/%s/%s-%s.jpg" % (
                                datetime.date.today(), photo_time, i)) for i in range(len(frame_list))]))
                    sense_data = device_gateway_pb2.StreamMessage(id=str(time.time()), payload=any)
                    logging.debug(sense_data)
                    self.return_cmd_queue.put(sense_data)

    def push_frames_to_server(self, request):
        logging.debug("push_frames_to_server: %s" % request)
        self._image_task_queue.put(request)

