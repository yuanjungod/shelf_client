# -*- coding: utf-8 -*-

from video_tool import VideoTool
import cv2
import threading
from lib import device_gateway_pb2
import time

import oss2


class Aliyun(object):

    # 以下代码展示了图片服务的基本用法。更详细应用请参看官网文档 https://help.aliyun.com/document_detail/32206.html

    # 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
    # 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
    #
    # 以杭州区域为例，Endpoint可以是：
    #   http://oss-cn-hangzhou.aliyuncs.com
    #   https://oss-cn-hangzhou.aliyuncs.com
    # 分别以HTTP、HTTPS协议访问。
    def __init__(self, queue):
        self.request_queue = queue
        self.sts_auth = None
        self.oss_bucket = None
        self.oss_endpoint = None
        self.account_info = None
        self.account_local_time = None
        self.bucket = None

    def set_aliyun(self, account_info):
        # print "set_aliyun", account_info
        self.account_info = account_info
        self.sts_auth = oss2.StsAuth(
            self.account_info.access_key_id, self.account_info.access_key_secret, self.account_info.security_token)
        self.oss_bucket = self.account_info.oss_bucket
        self.oss_endpoint = self.account_info.oss_endpoint
        self.account_local_time = time.time()
        # print "account_local_time", self.account_local_time

    def push_image2aliyun(self, remote_file_name, local_file_name):
        return self.bucket.put_object_from_file(remote_file_name, local_file_name)

    def check_account(self):
        if (self.account_info is None) or (
                self.account_info is not None and
                self.account_local_time + self.account_info.expires_in + 10 < time.time()):
            self.request_queue.put(device_gateway_pb2.AliyunFederationTokenRequest())
            # print self.account_local_time, self.account_info.expires_in

            while (self.account_info is None) or (self.account_local_time is None) or (
                    self.account_info is not None and self.account_local_time+self.account_info.expires_in + 10 < time.time()):
                time.sleep(0.5)
                # print "account_local_time", self.account_local_time
                print "account_info", self.account_info
        # print "account_info", self.account_info

    def push_image_2_aliyun(self, remote_file_name, image):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, encimg = cv2.imencode('.jpg', image, encode_param)
        # print image
        # print(dir(encimg))
        self.bucket = oss2.Bucket(self.sts_auth, self.oss_endpoint, self.oss_bucket)
        self.bucket.put_object(remote_file_name, encimg.tobytes())

    def push_batch_image_2_aliyun(self, remote_file_name_list, image_list):
        # self.check_account()
        threads = list()
        for i in range(len(remote_file_name_list)):
            threads.append(threading.Thread(target=self.push_image_2_aliyun, args=(remote_file_name_list[i], image_list[i])))
        for thread in threads:
            thread.start()
            thread.join()

