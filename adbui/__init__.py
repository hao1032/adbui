# coding=utf-8
from adbui.get_ui import GetUI
from adbui.util import Util
from adbui.adb_ext import AdbExt
from adbui.tango import Tango


class Device(GetUI):
    def __init__(self, sn=None):
        self.util = Util(sn)
        self.adb_ext = AdbExt(self.util)
        GetUI.__init__(self, self.adb_ext)
