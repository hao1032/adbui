# coding=utf-8
import logging
import os
import time
import random
import traceback
import requests
import json
import hmac
import hashlib
import binascii
import base64

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client, models


class Ocr(object):
    def __init__(self, keys):
        self.keys = keys
        self.app_id = None
        self.secret_id = None
        self.secret_key = None
        self.result = None
        os.environ['NO_PROXY'] = 'api.youtu.qq.com'  # 防止代理影响结果
        if len(keys) == 0:
            raise NameError('ocr appid or secret_id or secret_key is None')

    def __app_sign(self):
        now = int(time.time())
        expired = now + 2592000
        rdm = random.randint(0, 999999999)
        plain_text = 'a={}&k={}&e={}&t={}&r={}&u=xx&f='.format(self.app_id, self.secret_id, expired, now, rdm)
        b = hmac.new(self.secret_key.encode(), plain_text.encode(), hashlib.sha1)
        s = binascii.unhexlify(b.hexdigest()) + plain_text.encode('ascii')
        signature = base64.b64encode(s).rstrip()  # 生成签名
        return signature

    def __get_headers(self):
        sign = self.__app_sign()
        headers = {'Authorization': sign, 'Content-Type': 'text/json'}
        return headers

    def get_result_path(self, image_path):
        if len(image_path) == 0:
            return {'errormsg': 'IMAGE_PATH_EMPTY'}

        filepath = os.path.abspath(image_path)
        if not os.path.exists(filepath):
            return {'errormsg': 'IMAGE_FILE_NOT_EXISTS'}

        out = open(filepath, 'rb').read()
        return self.get_result(out)

    def get_result(self, image):
        self.result = None
        image = base64.b64encode(image)
        image = image.rstrip().decode('utf-8')

        for key in self.keys:  # 使用多个优图账号尝试,防止某个账号频率限制
            if 'error' not in key:
                key['error'] = 0  # 初始化碰到限制的次数
            if key['error'] > 3:
                continue  # 经常遇到频率限制的账号不用了
            self.app_id = key['app_id']
            self.secret_id = key['secret_id']
            self.secret_key = key['secret_key']
            headers = self.__get_headers()
            url = 'http://api.youtu.qq.com/youtu/ocrapi/generalocr'
            data = {"app_id": key['app_id'], "session_id": '', "image": image}

            try:
                r = requests.post(url, headers=headers, data=json.dumps(data))
                if r.status_code == 200:
                    r.encoding = 'utf-8'
                    self.result = r.json()
                    break
                else:
                    key['error'] = key['error'] + 1
                    logging.info('keys: {}'.format(self.keys))
                    logging.error('ocr请求返回异常:code {}, app_id {}'.format(r.status_code, key['app_id']))
            except Exception as e:
                traceback.print_exc()
                logging.error('error: {}'.format(traceback.format_exc()))

        if self.result and 'items' in self.result:
            return self.result
        else:
            logging.info('result:{}'.format(self.result))
            raise NameError('OCR 请求异常')


class TencentCloudOcr(object):
    def __init__(self, secret_id, secret_key):
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "ocr.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self.client = ocr_client.OcrClient(cred, "ap-guangzhou", clientProfile)

    def get_text_base_info(self, image):
        """
        通过图片的内容，获取图片上的文字内容
        :param image:
        :return:
        """
        req = models.GeneralFastOCRRequest()
        req.ImageBase64 = base64.b64encode(image).decode('utf-8')
        resp = self.client.GeneralFastOCR(req)
        logging.info('resp: {}'.format(resp.to_json_string()))
        return resp

    def get_result(self, image):
        """
        将腾讯云结果封装为优图结果，方便统一使用
        :param image:
        :return:
        """
        items = []
        resp = self.get_text_base_info(image)
        for info in resp.TextDetections:
            x = info.Polygon[0].X
            y = info.Polygon[0].Y
            width = info.Polygon[1].X - info.Polygon[0].X
            height = info.Polygon[3].Y - info.Polygon[0].Y
            box = {'x': x, 'y': y, 'width': width, 'height': height}
            items.append({'itemstring': info.DetectedText, 'itemcoord': box})
        return {'items': items}
