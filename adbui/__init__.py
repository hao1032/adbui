# coding=utf-8
from adbui.feature import Feature
from adbui.util import Util
from adbui.adb_ext import AdbExt


class Device(Feature):
    def __init__(self, sn=None):
        self.util = Util(sn)
        self.adb_ext = AdbExt(self.util)
        Feature.__init__(self, self.adb_ext)