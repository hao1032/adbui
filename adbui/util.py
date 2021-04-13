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
        self.is_wsl = 'linux' in platform.system().lower() and 'microsoft' in platform.release().lower()  # 判断当前是不是WSL环境
        self.is_py2 = sys.version_info < (3, 0)
        self.adb_path = ''
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
    def __get_cmd_process(arg):
        logging.debug(arg)
        p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # 将错误信息也使用stdout输出
        return p

    @staticmethod
    def __get_cmd_out(process):
        out, err = process.communicate()
        if err.strip():
            logging.error('命令 {} 有错误输出:\n{}'.format(process.args, err))

        return out

    @staticmethod
    def __run_cmd(arg, is_wait=True, encoding='utf-8', check_return_code=False):
        p = Util.__get_cmd_process(arg)
        if is_wait:
            out, err = p.communicate()
        else:
            return p  # 如果不等待，直接返回

        if encoding:
            out = out.decode(encoding)

        if check_return_code:
            p.communicate()  # 验证 return code，必须要结束
            if p.returncode != 0:  # 如果 returncode 非 0，引发异常
                raise NameError('{} 命令 return code {} 非 0\nout:\n{}'.format(arg, p.returncode, out))

        return out

    @staticmethod
    def cmd(arg, timeout=30, is_wait=True, encoding='utf-8', check_return_code=False):
        """
        执行命令，并返回命令的输出,有超时可以设置
        :param check_return_code:
        :param encoding:
        :param is_wait:
        :param arg:
        :param timeout:
        :return:
        """
        try:
            return func_timeout(timeout, Util.__run_cmd, args=(arg, is_wait, encoding, check_return_code))
        except FunctionTimedOut:
            print('执行命令超时 {}s: {}'.format(timeout, arg))

    def adb(self, arg, timeout=30, encoding='utf-8'):
        if self.adb_path == '' and self.is_wsl:  # 适配 wsl2 中使用 win10 中的adb情况
            out = Util.cmd('whereis adb')
            if 'adb:' in out:
                out = out.replace('adb:', '').strip().split(' /')[0]  # 使用第一个 path
                if 'adb' in out:
                    self.adb_path = '"{}"'.format(out)  # 防止有空格，加上双引号
        self.adb_path = self.adb_path if self.adb_path else 'adb'

        arg = '{} -s {} {}'.format(self.adb_path, self.sn, arg)
        return self.cmd(arg, timeout, encoding=encoding)

    def shell(self, arg, timeout=30, encoding='utf-8'):
        arg = 'shell {}'.format(arg)
        return self.adb(arg, timeout, encoding=encoding)
