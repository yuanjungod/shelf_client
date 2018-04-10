#! /usr/bin/env python
# -*- coding: utf-8 -*-
import grpc
from example import data_pb2, data_pb2_grpc
from lib.tools.video_tool import VideoTool
import time
import sqlite3
import datetime
import threading
import Queue
import cv2


class ShelfClient(object):

    def __init__(self, host, port):
        self._HOST = host
        self._PORT = port
        # self.video_tool = VideoTool("../models/haarcascades/haarcascade_frontalcatface.xml")
        # self.imgs = self.video_tool.convert_video_2_frame(0)
        self.conn = sqlite3.connect('user.db')
        self.quick_thread_cursor = self.conn.cursor()

        self.in_service = False
        self.slow_thread_control_queue = Queue.Queue()

        self.grpc_conn = grpc.insecure_channel(self._HOST + ':' + self._PORT)
        self.grpc_client = data_pb2_grpc.ShelfStub(channel=self.grpc_conn)

    def creat_db(self):
        self.quick_thread_cursor.execute('''CREATE TABLE EVENT
                       (ID INTEGER   PRIMARY KEY       AUTOINCREMENT,
                        TIME            TEXT       NOT NULL,
                        CMDTYPE         INT        NOT NULL,
                        CMDID           TEXT   NOT NULL,
                        IMAGELOCALURL   TEXT,
                        IMAGEREMOTEURL  TEXT,
                        STATUS          INT        NOT NULL);''')
        print "Table created successfully"
        self.conn.commit()
        # self.conn.close()

    def select_db(self):
        result = self.quick_thread_cursor.execute('''SELECT * FROM EVENT;''')
        print result.fetchall()
        print "Table created successfully"

    def service_prepare(self):
        self.open_light()

    def get_camera_frame(self):
        # img = self.imgs.next()
        return "0987654321"

    def push_image_to_ali(self, local_image_path):
        return True

    def get_device_status(self, cmd_type, cmd_id):
        return 0, 0, 0

    def get_door_status(self):
        return True

    def open_light(self):
        pass

    def close_light(self):
        pass

    def check_door_status(self):
        pass

    def device_status_change(self):
        return True

    def open_door_process(self, cmd_type, cmd_id):
        self.get_device_status(cmd_type, cmd_id)
        self.open_light()
        frame_local_path = self.get_camera_frame()
        SQL = "INSERT INTO EVENT (TIME, CMDTYPE, CMDID, IMAGELOCALURL, IMAGEREMOTEURL, STATUS) " \
              "VALUES ('%s', %s, '%s', '%s', '%s', '%s');" % (
                              datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f'),
                              cmd_type, cmd_id, frame_local_path, "aliyun/.1.jpg", 0)
        print(SQL)
        self.quick_thread_cursor.execute(SQL)
        self.conn.commit()
        print "Table insert successfully"
        return True

    def close_door_process(self, cmd_type, cmd_id):
        self.get_device_status(cmd_type, cmd_id)
        self.close_light()
        frame_local_path = self.get_camera_frame()
        SQL = "INSERT INTO EVENT (TIME, CMDTYPE, CMDID, IMAGELOCALURL, IMAGEREMOTEURL, STATUS) " \
              "VALUES ('%s', %s, '%s', '%s', '%s', '%s');" % (
                                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f'),
                                cmd_type, cmd_id, frame_local_path, "1.jpg", 0)
        print(SQL)
        self.quick_thread_cursor.execute(SQL)
        self.conn.commit()
        print "Table insert successfully"
        return True

    def slow_thread(self):
        self.slow_conn = sqlite3.connect('user.db')
        self.slow_thread_cursor = self.slow_conn.cursor()
        while True:
            print "slow_thread start"
            self.slow_thread_control_queue.get()
            print "slow thread "
            unfinish_event_list = self.slow_thread_cursor.execute("select * from EVENT where STATUS = 0")
            for unfinish_event in unfinish_event_list.fetchall():
                print unfinish_event
                if unfinish_event[6] == 0:
                    if self.push_image_to_ali(unfinish_event[1]):
                        response = self.grpc_client.Command(data_pb2.CommandReply(
                            cmd_type=1, cmd_id=str(1), image_url=""))
                        # while response.success != 1:
                        #     response = self.grpc_client.DoFormat(data_pb2.ShelfInfo(
                        #         cmd_type=1, cmd_id=str(1), image_url=""))
                        if response is not None:
                            self.slow_thread_cursor.execute("UPDATE EVENT SET STATUS = 1 WHERE TIME='%s'" % unfinish_event[1])
                            self.slow_conn.commit()

    def sent_to_web(self, buy_item):
        return True

    def process_cmd_type_0(self):
        response = self.grpc_client.Command(data_pb2.CommandReply(
            door_status=1, light_status=1, camera_status=1, next_service_ready=1))
        cmd_type = response.cmd_type
        cmd_id = response.cmd_id
        return cmd_type, cmd_id

    def process_cmd_type_1(self, cmd_id):
        stock_items = None
        buy_item = list()

        self.get_device_status(1, cmd_id)
        self.open_door_process(1, cmd_id)

        while self.get_door_status():
            self.push_image_to_ali("local_path")
            if stock_items is None:
                stock_items = self.grpc_client.Command(data_pb2.CommandReply(
                    door_status=1, light_status=1, camera_status=1, image_url="aliyun_path"))
            else:
                buy_item = stock_items - self.grpc_client.Command(data_pb2.CommandReply(
                    door_status=1, light_status=1, camera_status=1, image_url="aliyun_path"))
                self.sent_to_web(buy_item)

        if stock_items is not None:
            self.push_image_to_ali("local_path")
            buy_item = stock_items - self.grpc_client.Command(data_pb2.CommandReply(
                door_status=2, light_status=1, camera_status=1, image_url="aliyun_path"))
            self.sent_to_web(buy_item)

        # self.slow_thread_control_queue.put(True)
        #
        # self.close_door_process(cmd_type, cmd_id)
        #
        # self.slow_thread_control_queue.put(True)

        response = self.grpc_client.Command(data_pb2.CommandReply(
            cmd_type=1, door_status=2, light_status=2, camera_status=1, next_service_ready=1))
        cmd_type = response.cmd_type
        cmd_id = response.cmd_id
        return cmd_type, cmd_id

    def process_cmd_type_2(self, cmd_id):
        self.get_device_status(2, cmd_id)
        self.open_door_process(2, cmd_id)

        self.push_image_to_ali("local_path")
        self.grpc_client.Command(data_pb2.CommandReply(
            cmd_type=2, door_status=1, light_status=1, camera_status=1, image_url="aliyun_path"))

        while self.check_door_status():
            time.sleep(1)

        self.push_image_to_ali("local_path")
        self.grpc_client.Command(data_pb2.CommandReply(
                    door_status=2, light_status=1, camera_status=1, image_url="aliyun_path"))

        response = self.grpc_client.Command(data_pb2.CommandReply(
            door_status=2, light_status=2, camera_status=1, next_service_ready=1))
        cmd_type = response.cmd_type
        cmd_id = response.cmd_id
        return cmd_type, cmd_id

    def quick_thread(self):
        cmd_type = 0
        cmd_id = 0
        while True:
            if cmd_type == 0:
                cmd_type, cmd_id = self.process_cmd_type_0()
            elif cmd_type == 1:
                cmd_type, cmd_id = self.process_cmd_type_1(cmd_id)
            elif cmd_type == 2:
                cmd_type, cmd_id = self.process_cmd_type_2(cmd_id)


if __name__ == '__main__':
    shelf_client = ShelfClient('192.168.2.125', '9999')
    # shelf_client.select_db()

    # t = threading.Thread(target=shelf_client.slow_thread)
    # t.start()
    shelf_client.quick_thread()

    # time.sleep(10)


