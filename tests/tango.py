#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/29 3:58 上午
# @Author  : tangonian
# @Site    : 
# @File    : tango.py
# @Software: PyCharm
import subprocess
from lxml import etree
from adbui import Device
from adbui import Util
import logging
logging.basicConfig(level=logging.DEBUG)

d = Device('9EQUT20714008391')
# out = d.util.adb('version')
# print(out)

out = d.util.adb('devices')
print(out)