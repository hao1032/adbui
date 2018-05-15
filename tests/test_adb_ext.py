# coding=utf-8
import unittest
from adbui.util import Util
from adbui.adb_ext import AdbExt
from unittest.mock import MagicMock


class TestAdbExt(unittest.TestCase):
    def setUp(self):
        self.sn = '123abc'
        self.util = Util(self.sn)
        self.util.cmd = MagicMock()
        self.util.cmd.return_value = ''
        self.adb_ext = AdbExt(self.util)

    def tearDown(self):
        pass

    def test_dump(self):
        self.util.cmd.side_effect = NameError('dump xml fail!')
        self.adb_ext.dump()
        print(self.util.cmd.call_args_list)

