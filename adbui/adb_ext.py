# coding=utf-8
import os
import re
import tempfile


class AdbExt(object):
    def __init__(self, util):
        self.__util = util
        self.width, self.height = self.get_device_size()
        self.temp_name = 'temp_{}'.format(self.__util.sn)  # 临时文件名加上sn，防止多个手机多线程是有冲突
        self.temp_name = self.temp_name.replace('.', '').replace(':', '')  # 远程机器sn特殊，处理一下。如：10.15.34.56:11361
        self.temp_pc_dir_path = tempfile.gettempdir()
        self.temp_device_dir_path = '/data/local/tmp'

    def get_device_size(self):
        out = self.__util.shell('wm size')  # out like 'Physical size: 1080x1920'
        out = re.findall(r'\d+', out)
        return int(out[0]), int(out[1])  # width, height

    def get_pc_temp_name(self):
        return os.path.join(self.temp_pc_dir_path, self.temp_name)

    def dump(self, pc_name=None, pc_dir_path=None, device_path=None):
        pc_name = pc_name if pc_name else '{}.xml'.format(self.temp_name)
        pc_path, device_path = self.__get_pc_device_path(pc_name, pc_dir_path, device_path)  # 获取绝对路径
        self.delete_from_pc(pc_path)  # 删除电脑文件
        self.delete_from_device(device_path)  # 删除手机文件
        try_count = 5
        while try_count:  # 如果dump失败，多次尝试
            out = self.__util.shell('uiautomator dump {}'.format(device_path))
            if 'UI hierchary dumped to' in out:  # 如果dump成功，退出循环
                break
            else:  # 如果dump失败,重启 adb
                self.__util.adb('kill-server')
                self.__util.adb('start-server')
            try_count -= 1
        if try_count == 0:
            raise NameError('dump xml fail!')
        self.pull(pc_name, pc_dir_path, device_path)

    def delete_from_device(self, path):
        self.__util.shell('rm -rf {}'.format(path))

    def delete_from_pc(self, path):
        if os.path.exists(path): os.remove(path)

    def __get_pc_device_path(self, pc_name, pc_dir_path=None, device_path=None):
        pc_dir_path = pc_dir_path if pc_dir_path else self.temp_pc_dir_path
        pc_path = '"{}/{}"'.format(pc_dir_path, pc_name)
        device_path = device_path if device_path else '"{}/{}"'.format(self.temp_device_dir_path, pc_name)
        return pc_path, device_path

    def screenshot(self, pc_name=None, pc_dir_path=None, use_pull=True):
        pc_name = pc_name if pc_name else '{}.png'.format(self.temp_name)
        pc_path, device_path = self.__get_pc_device_path(pc_name, pc_dir_path, None)
        self.delete_from_pc(pc_path)  # 删除电脑文件
        self.delete_from_device(device_path)
        if use_pull:
            self.__util.shell('screencap -p {}'.format(device_path))
            self.__util.adb('pull {} {}'.format(device_path, pc_path))
            return
        arg = 'adb -s {} exec-out screencap -p'.format(self.__util.sn)
        self.__util.cmd_out_save(arg, pc_path, mode='wb')  # 这个命令可以直接将截图保存到电脑，节省了pull操作

    def pull(self, pc_name=None, pc_dir_path=None, device_path=None):
        pc_path, device_path = self.__get_pc_device_path(pc_name, pc_dir_path, device_path)
        self.__util.adb('pull {} {}'.format(device_path, pc_path))

    def push(self, pc_path=None, device_path=None):
        self.__util.adb('push "{}" "{}"'.format(pc_path, device_path))

    def click(self, x, y):
        self.__util.shell('input tap {} {}'.format(x, y))

    def long_click(self, x, y, duration=''):
        """
        长按
        :param x: x 坐标
        :param y: y 坐标
        :param duration: 长按的时间（ms）
        :return:
        """
        self.__util.shell('input touchscreen swipe {} {} {} {} {}'.format(x, y, x, y, duration))

    def start(self, pkg):
        """
        使用monkey，只需给出包名即可启动一个应用
        :param pkg:
        :return:
        """
        self.__util.shell('monkey -p {} 1'.format(pkg))

    def stop(self, pkg):
        self.__util.shell('am force-stop {}'.format(pkg))

    def input(self, text):
        self.__util.shell('input text "{}"'.format(text.replace('&', '\&')))

    def back(self, times=1):
        while times:
            self.__util.shell('input keyevent 4')
            times -= 1

    def home(self):
        self.__util.shell('input keyevent 3')

    def enter(self, times=1):
        while times:
            self.__util.shell('input keyevent 66')
            times -= 1

    def swipe(self, e1=None, e2=None, start_x=None, start_y=None, end_x=None, end_y=None, duration=" "):
        """
        滑动事件，Android 4.4以上可选duration(ms)
        usage: swipe(e1, e2)
               swipe(e1, end_x=200, end_y=500)
               swipe(start_x=0.5, start_y=0.5, e2)
        """
        if e1 is not None:
            start_x = e1[0]
            start_y = e1[1]
        if e2 is not None:
            end_x = e2[0]
            end_y = e2[1]
        if 0 < start_x < 1:
            start_x = start_x * self.width
        if 0 < start_y < 1:
            start_y = start_y * self.height
        if 0 < end_x < 1:
            end_x = end_x * self.width
        if 0 < end_y < 1:
            end_y = end_y * self.height

        self.__util.shell('input swipe %s %s %s %s %s' % (str(start_x), str(start_y), str(end_x), str(end_y), str(duration)))

    def clear(self, pkg):
        """
        重置应用
        :param pkg:
        :return:
        """
        self.__util.shell('pm clear {}'.format(pkg))

    def wake_up(self):
        """
        点亮屏幕
        :return:
        """
        self.__util.shell('input keyevent KEYCODE_WAKEUP')

    def unlock(self):
        """
        解锁屏幕
        :return:
        """
        self.__util.shell('input keyevent 82')

    def grant(self, pkg, permission):
        """
        给app赋权限，类似 adb shell pm grant [PACKAGE_NAME] android.permission.PACKAGE_USAGE_STATS
        :return:
        """
        self.__util.shell('pm grant {} {}'.format(pkg, permission))

    def install(self, apk_path, with_g=True, with_r=False):
        """
        安装包
        :param apk_path:
        :param with_g: -g 在一些设备上可以自动授权，默认 true
        :param with_r: -r 覆盖安装，默认 false
        :return:
        """
        arg = 'install'
        if with_g:
            arg = arg + ' -g'
        if with_r:
            arg = arg + ' -r'
        self.__util.adb('{} "{}"'.format(arg, apk_path))

    def uninstall(self, pkg):
        """
        卸载包
        :param pkg:
        :return:
        """
        self.__util.adb('uninstall {}'.format(pkg))
