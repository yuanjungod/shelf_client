# -*- coding: utf-8 -*-

from video_tool import VideoTool
from PIL import Image
import cv2
import threading
from gateway_proto import device_gateway_pb2
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
        self.bucket_name = None
        self.endpoint = None
        self.account_info = None

    def set_aliyun(self, account_info):
        self.account_info = account_info
        self.sts_auth = oss2.StsAuth(
            self.account_info.access_key_id, self.account_info.access_key_secret, self.account_info.security_token)
        self.bucket_name = self.account_info.bucket_name
        self.endpoint = self.account_info.endpoint

    def get_image_info(image_file):
        """获取本地图片信息
        :param str image_file: 本地图片
        :return tuple: a 3-tuple(height, width, format).
        """
        im = Image.open(image_file)
        return im.height, im.width, im.format

    def push_image2aliyun(self, remote_file_name, local_file_name):
        # 上传示例图片

        return self.bucket.put_object_from_file(remote_file_name, local_file_name)

    def push_image_2_aliyun(self, remote_file_name, image):
        if (self.account_info is None) or (self.account_info is not None and self.account_info.expires_in + 10 < time.time()):
            self.request_queue.put(device_gateway_pb2.AliyunFederationTokenRequest)
            while self.account_info is None or self.account_info.expires_in + 10 < time.time():
                time.sleep(0.5)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, encimg = cv2.imencode('.jpg', image, encode_param)
        # print(dir(encimg))
        self.bucket = oss2.Bucket(self.sts_auth, self.endpoint, self.bucket_name)
        self.bucket.put_object(remote_file_name, encimg.tobytes())

    def push_batch_image_2_aliyun(self, remote_file_name_list, image_list):
        threads = list()
        for i in range(len(remote_file_name_list)):
            threads.append(threading.Thread(target=self.push_image_2_aliyun, args=(remote_file_name_list[i], image_list[i])))
        for thread in threads:
            thread.start()
            thread.join()


if __name__ == "__main__":
    aliyun_tool = Aliyun("STS.LTLsqh2ZHvD8sUSDXWpjoDSS7", "3iovSbH1bbM18YNnsqxdbye1Zbgzz89ZvYp8ERj7iJgd",
                         "object-detect-test", "xxxx-xxxx-xxxx-xxxx/3031be84750e96a30a549cfafc3e7bb6/20180413")
    frames = VideoTool.convert_video_2_frame(0)
    count = 1
    for frame in frames:

        print count, frame.shape
        aliyun_tool.push_image_2_aliyun("%s.jpg" % count, frame)
        count += 1
    # aliyun_tool.bucket.get_object_to_file('1.jpg', '1.jpg')
    # print aliyun_tool.push_image2aliyun("authentication.png", "/Users/quantum/Downloads/123.png")
