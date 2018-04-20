# coding=utf-8
import os
import tempfile


class AdbExt(object):
    def __init__(self, util):
        self.__util = util
        self.temp_name = 'temp'  # 如果是多个进程，可以修改这个变量，保证多个手机在pc上的文件不会冲突
        self.temp_pc_dir_path = tempfile.gettempdir()
        self.temp_device_dir_path = '/data/local/tmp'

    def get_pc_temp_name(self):
        return os.path.join(self.temp_pc_dir_path, self.temp_name)

    def dump(self, pc_name=None, pc_dir_path=None, device_path=None):
        pc_name = pc_name if pc_name else '{}.xml'.format(self.temp_name)
        pc_path, device_path = self.__get_pc_device_path(pc_name, pc_dir_path, device_path)  # 获取绝对路径
        self.delete_from_pc(pc_path)  # 删除电脑文件
        self.delete_from_device(device_path)  # 删除手机文件
        try_count = 3
        while try_count:  # 如果dump失败，多次尝试
            out = self.__util.shell('uiautomator dump {}'.format(device_path))
            if 'UI hierchary dumped to' in out:  # 如果dump成功，退出循环
                break
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
        pc_path = '{}/{}'.format(pc_dir_path, pc_name)
        device_path = device_path if device_path else '{}/{}'.format(self.temp_device_dir_path, pc_name)
        return pc_path, device_path

    def screenshot(self, pc_name=None, pc_dir_path=None):
        pc_name = pc_name if pc_name else '{}.png'.format(self.temp_name)
        pc_path, device_path = self.__get_pc_device_path(pc_name, pc_dir_path, None)
        self.delete_from_pc(pc_path)  # 删除电脑文件
        arg = 'adb -s {} exec-out screencap -p'.format(self.__util.sn)
        self.__util.cmd_out_save(arg, pc_path, mode='wb')  # 这个命令可以直接将截图保存到电脑，节省了pull操作

    def pull(self, pc_name=None, pc_dir_path=None, device_path=None):
        pc_path, device_path = self.__get_pc_device_path(pc_name, pc_dir_path, device_path)
        self.__util.adb('pull {} {}'.format(device_path, pc_path))

    def click(self, x, y):
        self.__util.shell('input tap {} {}'.format(x, y))

    def stop(self, pkg):
        self.__util.shell('am force-stop {}'.format(pkg))

    def input(self, text):
        self.__util.shell('input text "{}"'.format(text.replace('&', '\&')))

    def back(self, times=1):
        while times:
            self.__util.shell('input keyevent 4')
            times -= 1

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

        self.__util.shell(
            "input swipe %s %s %s %s %s" % (str(start_x), str(start_y), str(end_x), str(end_y), str(duration)))

    def clear(self, pkg):
        """
        重置应用
        :param pkg:
        :return:
        """
        self.__util.shell('pm clear {}'.format(pkg))

    def wake_up(self):
        '''
        点亮屏幕
        :return:
        '''
        self.__util.shell('input keyevent KEYCODE_WAKEUP')
