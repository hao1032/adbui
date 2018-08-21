# coding=utf-8
import re
import os
import platform
import subprocess
import signal
import time


class Util(object):
    def __init__(self, sn):
        self.sn = sn
        if sn is None:
            self.sn = self.__get_sn()

    def __get_sn(self):
        out = self.cmd('adb devices').strip()
        out = re.split(r'[\r\n]+', out)
        for line in out[1:]:
            if not line.strip():
                continue
            if 'offline' in line:
                print(line)
                continue
            sn, _ = re.split(r'\s+', line, maxsplit=1)
            return sn
        raise NameError('没有手机连接 (No device connected)')
        
    def cmd(self, arg, timeout=30):
        """
        执行命令，并返回命令的输出,有超时可以设置
        :param arg:
        :param timeout:
        :return:
        """
        is_linux = platform.system() == 'Linux'
        # print(arg)
        p = subprocess.Popen(arg, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True,
                             preexec_fn=os.setsid if is_linux else None)
        start = time.time()
        while True:
            if p.poll() is not None:
                break
            seconds_passed = time.time() - start
            if timeout and seconds_passed > timeout:
                if is_linux:
                    os.killpg(p.pid, signal.SIGTERM)
                else:
                    p.terminate()
                raise TimeoutError(arg, timeout)
            time.sleep(0.2)
        out = p.stdout.read().decode('utf-8').strip()
        return out
    
    def cmd_out_save(self, arg, pc_path, mode='a'):
        """
        将命令的输出保存到文件
        :param arg: 命令
        :param pc_path: 保存路径
        :param mode: 保存模式，默认是追加
        :return: 
        """
        with open(pc_path, mode) as f:
            subprocess.call(arg, stdout=f)

    def adb(self, arg, timeout=30):
        arg = 'adb -s {} {}'.format(self.sn, arg)
        return self.cmd(arg, timeout)

    def shell(self, arg, timeout=30):
        arg = 'shell {}'.format(arg)
        return self.adb(arg, timeout)
