#! /usr/bin/env python
# -*- coding: utf-8 -*-
import grpc
import time
from concurrent import futures
from example import data_pb2, data_pb2_grpc
import cv2
import json
import numpy as np


_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_HOST = '192.168.2.30'
_PORT = '9999'

count = 1


class FormatData(data_pb2_grpc.FormatDataServicer):
    def DoFormat(self, request, context):
        global count
        # print(request.image.decode('iso-8859-1'))
        # print(type(request.image.encode()))
        # img = cv2.imdecode(np.array(json.loads(request.image.encode())), cv2.IMREAD_COLOR)
        # if count > 20 and count % 5 == 0:
        #     print(img)
        #     cv2.imwrite("%s.jpg" % count, img)
        count += 1

        return data_pb2.CMDInfo(cmd_type=1)


def serve():
    grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    data_pb2_grpc.add_FormatDataServicer_to_server(FormatData(), grpcServer)
    grpcServer.add_insecure_port(_HOST + ':' + _PORT)
    grpcServer.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        grpcServer.stop(0)


if __name__ == '__main__':
    serve()

