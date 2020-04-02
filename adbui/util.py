# coding=utf-8
import re
import sys
import subprocess
import logging
import platform
from func_timeout import func_timeout, FunctionTimedOut


class Util(object):
    def __init__(self, sn):
        self.is_win = 'window' in platform.system().lower()
        self.is_wsl = 'Linux' in platform.system() and 'Microsoft' in platform.release()  # 判断当前是不是WSL环境
        self.is_py2 = sys.version_info < (3, 0)
        self.sn = sn
        self.debug = False
        if sn is None:
            self.sn = self.get_sn_list()[0]

    @staticmethod
    def get_sn_list():
        out = Util.cmd('adb devices').strip()
        out = re.split(r'[\r\n]+', out)
        sn_list = []
        for line in out[1:]:
            if not line.strip():
                continue
            if 'offline' in line:
                logging.warning('离线设备:{}'.format(line))
                continue
            sn, _ = re.split(r'\s+', line, maxsplit=1)
            sn_list.append(sn)
        if sn_list:
            return sn_list
        else:
            raise NameError('没有手机连接 (No device connected)')

    @staticmethod
    def __run_cmd(arg, is_bytes):
        logging.debug(arg)
        out = subprocess.check_output(arg, shell=True, stderr=subprocess.STDOUT)  # 将错误信息也使用stdout输出
        if not is_bytes:
            out = out.decode('utf-8')
        return out

    @staticmethod
    def cmd(arg, timeout=30, is_bytes=False):
        """
        执行命令，并返回命令的输出,有超时可以设置
        :param is_bytes:
        :param arg:
        :param timeout:
        :return:
        """
        try:
            out = func_timeout(timeout, Util.__run_cmd, args=(arg, is_bytes))
            return out
        except FunctionTimedOut:
            print('执行命令超时:{}s {}'.format(timeout, arg))

    def adb(self, arg, timeout=30):
        arg = 'adb -s {} {}'.format(self.sn, arg)
        return self.cmd(arg, timeout)

    def shell(self, arg, timeout=30):
        arg = 'shell {}'.format(arg)
        return self.adb(arg, timeout)
