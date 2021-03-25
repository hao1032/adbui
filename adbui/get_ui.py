# coding=utf-8
import sys
import re
import logging
import traceback
from lxml import etree
from .ocr import Ocr
from lxml.etree import tostring

short_keys = {'id': 'resource-id', 'class_': 'class', 'klass': 'class', 'desc': 'content-desc'}


class GetUI(object):
    def __init__(self, adb_ext):
        self.adb_ext = adb_ext
        self.keys = None
        self.xml = None
        self.ocr = None
        self.init_ocr()
        self.image = None

    def init_ocr(self, app_id=None, secret_id=None, secret_key=None, keys=[]):
        self.keys = keys
        if app_id is None and secret_id is None and secret_key is None:
            # 以下为测试账号，任何人可用，但是随时都会不可用，建议自行去腾讯优图申请专属账号
            app_id = '10126986'
            secret_id = 'AKIDT1Ws34B98MgtvmqRIC4oQr7CBzhEPvCL'
            secret_key = 'AAyb3KQL5d1DE4jIMF2f6PYWJvLaeXEk'
        self.keys.append({'app_id': app_id, 'secret_id': secret_id, 'secret_key': secret_key})
        self.ocr = Ocr(app_id, secret_id, secret_key)

    def get_ui_by_attr(self, is_contains=True, is_update=True, **kwargs):
        uis = self.get_uis_by_attr(is_contains=is_contains, is_update=is_update, **kwargs)
        return uis[0] if uis else None

    def get_uis_by_attr(self, is_contains=True, is_update=True, **kwargs):
        """
        通过节点的属性获取节点
        :param is_contains: 是否使用模糊查找
        :param is_update:
        :param kwargs:
        :return: 
        """
        for key in list(kwargs):
            if key in short_keys:
                kwargs[short_keys[key]] = kwargs.pop(key)
        if is_contains:
            s = list(map(lambda x: "contains(@{}, '{}')".format(x, kwargs[x]), kwargs))
            xpath = './/*[{}]'.format(' and '.join(s))
        else:
            s = list(map(lambda key: "[@{}='{}']".format(key, kwargs[key]), kwargs))
            xpath = './/*{}'.format(''.join(s))
        uis = self.get_uis_by_xpath(xpath, is_update=is_update)
        return uis

    def get_ui_by_xpath(self, xpath, is_update=True):
        uis = self.get_uis_by_xpath(xpath, is_update)
        return uis[0] if uis else None

    def get_uis_by_xpath(self, xpath, is_update=True):
        """
        通过xpath查找节点
        :param xpath: 
        :param is_update: 
        :return: 
        """
        if is_update:
            xml_str = None
            for _ in range(5):
                try:
                    xml_str = self.adb_ext.dump()  # 获取xml文件
                    self.__init_xml(xml_str)
                    break
                except etree.XMLSyntaxError:
                    traceback.print_exc()
                    logging.error('etree.XMLSyntaxError:\n')
                    if xml_str:
                        logging.error(xml_str)
                        logging.error('xml str:{}'.format(xml_str))
        xpath = xpath.decode('utf-8') if sys.version_info[0] < 3 else xpath
        elements = self.xml.xpath(xpath)
        uis = []
        for element in elements:
            uis.append(self.get_ui_by_element(element))
        return uis

    def get_ui_by_element(self, element):
        bounds = element.get('bounds')
        x1, y1, x2, y2 = re.compile(r"-?\d+").findall(bounds)
        ui = UI(self.adb_ext, x1, y1, x2, y2)
        ui.element = element
        text = element.get('text')
        if not text:
            text = element.get('content-desc')
        ui.text = text.encode('utf-8') if self.adb_ext.util.is_py2 and not isinstance(text, str) else text
        return ui

    def get_ui_by_ocr(self, text, is_contains=True, is_update=True):
        uis = self.get_uis_by_ocr(text, is_contains, is_update)
        return uis[0] if uis else None

    def get_uis_by_ocr(self, text, is_contains=True, is_update=True):
        """
        通过ocr识别获取节点
        :param is_contains:
        :param text: 查找的文本
        :param is_update: 是否重新获取截图
        :return: 
        """
        if self.ocr is None:
            raise NameError('ocr 功能没有初始化.请到 adbui 页面查看如何使用。\nhttps://github.com/hao1032/adbui')
        if is_update:
            self.image = self.adb_ext.screenshot(is_jpg=True)  # 获取截图

        ocr_result = self.__get_ocr_result()
        text = text.decode('utf-8') if self.adb_ext.util.is_py2 and isinstance(text, str) else text
        uis = []
        for item in ocr_result['items']:
            item_string = item['itemstring']
            item_string = item_string.decode('utf-8') if self.adb_ext.util.is_py2 and isinstance(item_string, str) else item_string

            if (is_contains and text in item_string) or (not is_contains and text == item_string):
                item_coord = item['itemcoord']
                ui = UI(self.adb_ext, item_coord['x'], item_coord['y'],
                        item_coord['x'] + item_coord['width'], item_coord['y'] + item_coord['height'])
                ui.text = item_string
                uis.append(ui)
        return uis

    def __get_ocr_result(self):
        for key in self.keys:
            ocr_result = self.ocr.get_result_image(self.image)
            if 'httpcode' in ocr_result and ocr_result['httpcode'] == 510:  # 如果频率限制，换一个
                self.ocr = Ocr(app_id=key['app_id'], secret_id=key['secret_id'], secret_key=key['secret_key'])
            else:
                return ocr_result

        if 'httpcode' in ocr_result and ocr_result['httpcode'] == 510:  # 如果依然频率限制，报错
            raise NameError('OCR 服务调用频率限制或者连接数限制，请使用自己申请的账号。')

    def __init_xml(self, xml_str):
        # if not isinstance(xml_str, str):
        #     xml_str = xml_str.encode('utf-8')
        parser = etree.XMLParser(huge_tree=True)
        self.xml = etree.fromstring(xml_str, parser=parser)
        for element in self.xml.findall('.//node'):
            element.tag = element.get('class').split('.')[-1].replace('$', '')  # 将每个node的name替换为class值，和uiautomator里显示的一致

        try:
            self.original_xml = etree.tostring(self.xml, pretty_print=True, encoding='utf-8').decode()  # 原始 xml
            self.replace_xml = etree.tostring(self.xml, pretty_print=True, encoding='utf-8').decode()  # 替换后的 xml
        except:
            self.replace_xml = etree.tostring(self.xml, pretty_print=True).decode()  # 替换后的 xml
            self.original_xml = etree.tostring(self.xml, pretty_print=True).decode()  # 原始 xml


class UI:
    def __init__(self, adb_ext, x1, y1, x2, y2):
        self.__adb_ext = adb_ext
        self.x1 = int(x1)  # 左上角 x
        self.y1 = int(y1)  # 左上角 y
        self.x2 = int(x2)  # 右下角 x
        self.y2 = int(y2)  # 右下角 y
        self.width = self.x2 - self.x1  # 元素宽
        self.height = self.y2 - self.y1  # 元素高
        self.x = self.x1 + int(self.width / 2)
        self.y = self.y1 + int(self.height / 2)
        self.text = None  # 元素文本
        self.element = None  # 元素对应的 lxml element，ocr无效

    def get_element_str(self):
        return tostring(self.element)

    def get_value(self, key):
        # 返回 lxml element 属性对应的值
        if key in short_keys:
            key = short_keys[key]
        return self.element.get(key)

    def click(self):
        # 点击元素的中心点
        self.__adb_ext.click(self.x, self.y)
