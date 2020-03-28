#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/29 3:58 上午
# @Author  : tangonian
# @Site    : 
# @File    : tango.py
# @Software: PyCharm
from adbui import Device

d = Device()
n = d.adb_ext.get_name(True)
print(n)