# coding=utf-8
import os
import sys
import time
import random
import requests
import json
import hmac, hashlib
import binascii
import base64
if sys.version_info[0] < 3:
    from cStringIO import StringIO as BytesIO
else:
    from io import BytesIO


class Ocr(object):
    def __init__(self, app_id=None, secret_id=None, secret_key=None):
        self.user_id = 'xx'
        self.result = None
        if app_id and secret_key and secret_key:
            os.environ['NO_PROXY'] = 'api.youtu.qq.com'  # 防止代理影响结果
            self.app_id = app_id
            self.secret_id = secret_id
            self.secret_key = secret_key
        else:
            raise NameError('ocr appid or secret_id or secret_key is None')

    def __app_sign(self, expired=0):
        now = int(time.time())
        rdm = random.randint(0, 999999999)
        plain_text = 'a=' + self.app_id + '&k=' + self.secret_id + '&e=' + str(expired) + '&t=' + str(
            now) + '&r=' + str(rdm) + '&u=' + self.user_id + '&f='
        b = hmac.new(self.secret_key.encode(), plain_text.encode(), hashlib.sha1)
        s = b.hexdigest()
        s = binascii.unhexlify(s)
        s = s + plain_text.encode('ascii')
        signature = base64.b64encode(s).rstrip()  # 生成签名
        return signature

    def __get_headers(self):
        expired = int(time.time()) + 2592000
        sign = self.__app_sign(expired)
        headers = {'Authorization': sign, 'Content-Type': 'text/json'}
        return headers

    def get_result_path(self, image_path):
        if len(image_path) == 0:
            return {'httpcode': 0, 'errormsg': 'IMAGE_PATH_EMPTY'}

        filepath = os.path.abspath(image_path)
        if not os.path.exists(filepath):
            return {'httpcode': 0, 'errormsg': 'IMAGE_FILE_NOT_EXISTS'}
        image = base64.b64encode(open(filepath, 'rb').read())
        return self.__get_result(image)

    def get_result_image(self, image):
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        image = base64.b64encode(buffered.getvalue())
        return self.__get_result(image)

    def __get_result(self, image):
        headers = self.__get_headers()
        url = 'http://api.youtu.qq.com/youtu/ocrapi/generalocr'
        data = {"app_id": self.app_id, "session_id": '', "image": image.rstrip().decode('utf-8')}

        try:
            r = requests.post(url, headers=headers, data=json.dumps(data))
            if r.status_code != 200:
                return {'httpcode': r.status_code, 'errorcode': '', 'errormsg': ''}
            r.encoding = 'utf-8'
            self.result = r.json()
            return self.result
        except Exception as e:
            return {'httpcode': 0, 'errorcode': 'IMAGE_NETWORK_ERROR', 'errormsg': str(e)}


