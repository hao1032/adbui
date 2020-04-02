# coding=utf-8
from adbui.get_ui import GetUI
from adbui.util import Util as BaseUtil
from adbui.adb_ext import AdbExt
from adbui.tango import Tango


class Device(GetUI):
    def __init__(self, sn=None):
        self.util = BaseUtil(sn)
        self.adb_ext = AdbExt(self.util)
        GetUI.__init__(self, self.adb_ext)


class Util(BaseUtil):
    pass
