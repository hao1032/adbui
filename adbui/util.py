# coding=utf-8
import re
import sys
import subprocess
import logging
import platform
import time
import traceback

from func_timeout import func_timeout, FunctionTimedOut


class Util(object):
    def __init__(self, sn):
        self.is_win = 'window' in platform.system().lower()
        self.is_wsl = 'linux' in platform.system().lower() and 'microsoft' in platform.release().lower()  # 判断当前是不是WSL环境
        self.is_py2 = sys.version_info < (3, 0)
        self.sn = sn
        self.adb_path = None
        self.debug = False

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
    def __run_cmd(arg, is_wait=True, encoding='utf-8'):
        p = Util.__get_cmd_process(arg)
        if is_wait:
            out, err = p.communicate()
        else:
            return p  # 如果不等待，直接返回

        if err:
            logging.error('err: {}, arg: {}'.format(err.strip(), arg))

        if encoding:
            out = out.decode(encoding)
            err = err.decode(encoding)

        try:
            logging.debug('out[: 100]: {}'.format(out[: 100].strip()))
        except Exception as e:
            error_str = traceback.format_exc().strip()
            logging.debug('out log error: {}'.format(error_str))

        return out, err

    @staticmethod
    def cmd(arg, timeout=30, is_wait=True, encoding='utf-8'):
        """
        执行命令，并返回命令的输出,有超时可以设置
        :param arg:
        :param timeout:
        :param is_wait:
        :param encoding:
        :return:
        """
        try:
            return func_timeout(timeout, Util.__run_cmd, args=(arg, is_wait, encoding))
        except FunctionTimedOut:
            print('执行命令超时 {}s: {}'.format(timeout, arg))

    def adb(self, arg, timeout=30, encoding='utf-8'):
        self.adb_path = self.adb_path if self.adb_path and self.adb_path != 'adb' else 'adb'

        if not self.sn:
            self.sn = self.get_first_sn()

        arg = '{} -s {} {}'.format(self.adb_path, self.sn, arg)
        for index in range(3):
            result = self.cmd(arg, timeout, encoding=encoding)

            if result is not None and len(result) == 2:
                out, err = result
            else:
                logging.error('执行 cmd 返回结果异常：{}'.format(result))
                continue

            if err:  # 错误处理
                if isinstance(err, bytes):
                    err = err.decode('utf-8')

                # 处理设备连接错误
                is_device_not_found = 'device' in err and 'not found' in err
                is_device_offline = 'device offline' in err
                if is_device_not_found or is_device_offline:
                    if index == 2:
                        raise NameError('设备无法使用: {}'.format(self.sn))
                    self.connect_sn()  # 尝试重新连接网络设备

                else:  # 只处理某些错误
                    return out
            else:  # 没有错误，返回命令的结果
                return out
        assert False, 'adb run error: {}'.format(arg)

    def shell(self, arg, timeout=30, encoding='utf-8'):
        arg = 'shell {}'.format(arg)
        return self.adb(arg, timeout, encoding=encoding)

    def connect_sn(self):
        if self.sn.count('.') != 3:
            return  # 非网络设备不处理
        self.cmd('adb disconnect {}'.format(self.sn))  # 首先断开连接，排除该 sn 当前是 offline 状态
        time.sleep(1)  # 等待断开
        self.cmd('adb connect {}'.format(self.sn))
        time.sleep(1)  # 等待连接

        info = self.get_sn_info()
        logging.info('连接后的设备列表：{}'.format(info))

    def get_first_sn(self):
        sn_info = self.get_sn_info()
        for sn in sn_info:
            if sn_info[sn] == 'device':
                return sn
        raise NameError('没有可以使用的设备: {}'.format(sn_info))

    def get_sn_info(self):
        sn_info = {}
        out, err = self.cmd('adb devices')
        lines = re.split(r'[\r\n]+', out.strip())
        for line in lines[1:]:
            if not line.strip():
                continue
            sn, status = re.split(r'\s+', line, maxsplit=1)
            sn_info[sn] = status
        return sn_info
