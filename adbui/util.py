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
    def __run_cmd(arg, want_bytes):
        logging.debug(arg)
        out = subprocess.check_output(arg, shell=True)
        if not want_bytes:
            out = out.decode('utf-8')
        return out

    @staticmethod
    def cmd(arg, timeout=30, want_bytes=False):
        """
        执行命令，并返回命令的输出,有超时可以设置
        :param want_bytes:
        :param arg:
        :param timeout:
        :return:
        """
        try:
            out = func_timeout(timeout, Util.__run_cmd, args=(arg, want_bytes))
            return out
        except FunctionTimedOut:
            print('执行命令超时:{}s {}'.format(timeout, arg))

    def adb(self, arg, timeout=30):
        arg = 'adb -s {} {}'.format(self.sn, arg)
        return self.cmd(arg, timeout)

    def shell(self, arg, timeout=30):
        arg = 'shell {}'.format(arg)
        return self.adb(arg, timeout)

    def cmd_out_save(self, arg, pc_path, mode='a'):
        """
        将命令的输出保存到文件
        :param arg: 命令
        :param pc_path: 保存路径
        :param mode: 保存模式，默认是追加
        :return:
        """
        logging.debug('{} > "{}"'.format(arg, pc_path))
        want_bytes = 'b' in mode
        out = self.cmd(arg, want_bytes=want_bytes)

        if pc_path is None:
            return out

        if self.is_win:
            pc_path = pc_path.decode('utf-8')  # 适配win机器
        with open(pc_path, mode) as f:
            f.write(out)
            return True
        return False
