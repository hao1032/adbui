# coding=utf-8
import os
import unittest
import warnings
import tempfile
from adbui.util import Util
from unittest.mock import MagicMock


class TestUtil(unittest.TestCase):
    def setUp(self):
        self.sn = '123abc'
        self.util = Util(self.sn)
        self.path = os.path.join(tempfile.gettempdir(), 'temp.txt')
        if os.path.exists(self.path): os.remove(self.path)

    def tearDown(self):
        if os.path.exists(self.path): os.remove(self.path)

    def test_cmd(self):
        warnings.simplefilter("ignore")
        self.assertEqual(self.util.cmd('echo adbui'), 'adbui')

    def test_cmd_out_save(self):
        self.util.cmd_out_save('echo adbui', self.path)
        self.assertTrue(os.path.exists(self.path))
        self.assertFalse(not os.path.exists(self.path))

    def test_adb(self):
        self.util.cmd = MagicMock()
        self.util.cmd.return_value = None
        self.util.adb('adbui')
        self.util.cmd.assert_called_once_with('adb -s 123abc adbui')

    def test_shell(self):
        self.util.cmd = MagicMock()
        self.util.cmd.return_value = None
        self.util.shell('adbui')
        self.util.cmd.assert_called_once_with('adb -s 123abc shell adbui')

