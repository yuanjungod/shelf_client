# -*- coding: utf-8 -*-

import json
import os

from PIL import Image

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
    def __init__(self):
        access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', '<你的AccessKeyId>')
        access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', '<你的AccessKeySecret>')
        bucket_name = os.getenv('OSS_TEST_BUCKET', '<你的Bucket>')
        endpoint = os.getenv('OSS_TEST_ENDPOINT', '<你的访问域名>')

        # 确认上面的参数都填写正确了
        for param in (access_key_id, access_key_secret, bucket_name, endpoint):
            assert '<' not in param, '请设置参数：' + param

        # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
        self.bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)

    def get_image_info(image_file):
        """获取本地图片信息
        :param str image_file: 本地图片
        :return tuple: a 3-tuple(height, width, format).
        """
        im = Image.open(image_file)
        return im.height, im.width, im.format

    # def push_images_to_aliyun(self, remote_image_list):

    def push_image2aliyun(self, remote_file_name, local_file_name):
        # 上传示例图片
        return self.bucket.put_object_from_file(remote_file_name, local_file_name)