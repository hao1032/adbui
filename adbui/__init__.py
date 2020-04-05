# coding=utf-8
from .get_ui import GetUI
from .util import Util
from .adb_ext import AdbExt
from .tango import Tango


class Device(GetUI):
    def __init__(self, sn=None):
        self.util = Util(sn)
        self.adb_ext = AdbExt(self.util)
        GetUI.__init__(self, self.adb_ext)
