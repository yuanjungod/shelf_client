#! /usr/bin/env python
# -*- coding: utf-8 -*-
import grpc
from example import data_pb2, data_pb2_grpc
from lib.tools.video_tool import VideoTool
import cv2
import time
import json
import numpy as np
import json
import struct

_HOST = '192.168.2.30'
_PORT = '9999'

video_tool = VideoTool("../models/haarcascades/haarcascade_frontalcatface.xml")
imgs = video_tool.convert_video_2_frame(0)


def run():
    conn = grpc.insecure_channel(_HOST + ':' + _PORT)
    client = data_pb2_grpc.FormatDataStub(channel=conn)
    # print(type(data_pb2.ShelfInfo))
    img = imgs.next()
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
    result, encimg = cv2.imencode('.jpg', img, encode_param)
    # print(dir(encimg))
    img_str = encimg.tobytes()
    # print(dir(encimg))
    print(dir(encimg.data))
    # print(type(struct.pack(img_str)))

    # values = (1, 'abc', 2.7)
    # s = struct.Struct('I3sf')
    # packed_data = s.pack(*values)
    # unpacked_data = s.unpack(packed_data)
    # print(type(packed_data))

    response = client.DoFormat(data_pb2.ShelfInfo(door_status=0, light_status=0, camera_status=-1, image=img_str))
    print("received: " + str(response.cmd_type))


if __name__ == '__main__':
    while True:
        run()
        # time.sleep(10)


