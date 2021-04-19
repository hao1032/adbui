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

d = Device()


d.util.shell('time 1')
