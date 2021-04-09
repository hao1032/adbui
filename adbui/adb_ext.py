# coding=utf-8
import os
import re
import time
import tempfile
from io import BytesIO
from PIL import Image


class AdbExt(object):
    def __init__(self, util):
        self.util = util
        if self.util.is_py2:
            from cStringIO import StringIO as BytesIO
        self.width, self.height = self.get_device_size()
        self.temp_name = 'temp_{}'.format(self.util.sn)  # 临时文件名加上sn，防止多个手机多线程是有冲突
        self.temp_name = self.temp_name.replace('.', '').replace(':', '')  # 远程机器sn特殊，处理一下。如：10.15.34.56:11361
        self.temp_pc_dir_path = tempfile.gettempdir()
        self.temp_device_dir_path = '/data/local/tmp'

    def get_device_size(self):
        out = self.util.shell('wm size')  # out like 'Physical size: 1080x1920'
        out = re.findall(r'\d+', out)
        return int(out[0]), int(out[1])  # width, height

    def dump(self):
        for i in range(5):
            out = self.util.adb('exec-out uiautomator dump --compressed /dev/tty', encoding='')  # 优先使用压缩模式
            start = out.find(b'<?xml')
            if start < 0:
                out = self.util.adb('exec-out uiautomator dump /dev/tty', encoding='')  # 失败后使用正常模式
                start = out.find(b'<?xml')

            end = out.find(b'</hierarchy>') + len(b'</hierarchy>')
            if start >= 0 and end > 0:  # 检查是否有xml文档
                out = out[start: end]  # 去掉xml前后的内容
                return out
        raise NameError('dump xml fail!')

    def get_pc_temp_name(self):
        return os.path.join(self.temp_pc_dir_path, self.temp_name)

    def delete_from_device(self, path):
        self.util.shell('rm -rf {}'.format(path))

    def delete_from_pc(self, path):
        if os.path.exists(path):
            os.remove(path)

    def screenshot(self, pc_path=None, pil_image=True, is_jpg=False, quality=65):
        if pc_path:
            if self.util.is_py2:
                pc_path = pc_path.decode('utf-8')
            self.delete_from_pc(pc_path)  # 删除电脑文件

            _, ext = os.path.splitext(pc_path)
            folder_path, _ = os.path.split(pc_path)
            if folder_path and not os.path.isdir(folder_path):
                os.makedirs(folder_path)

            if ext.lower() in ['.jpg', '.jpeg']:  # 根据后缀判断格式
                is_jpg = True

        arg = 'adb -s {} exec-out screencap -p'.format(self.util.sn)
        image = self.util.cmd(arg, encoding=None)  # 这里是 png bytes string

        if is_jpg:  # jpg 格式需要pil image 格式才可以
            pil_image = True

        if pc_path and not is_jpg:  # 直接保存为png图片
            with open(pc_path, 'wb') as f:
                f.write(image)

        if pil_image:  # 转换为 pil 图片对象
            image = Image.open(BytesIO(image))

        if pil_image and is_jpg:  # 转换为jpg格式
            image = image.convert('RGB')

        if pc_path and is_jpg:  # 保存为jpg
            image.save(pc_path, 'JPEG', optimize=True, quality=quality)

        return image

    def pull(self, device_path=None, pc_path=None):
        self.util.adb('pull "{}" "{}"'.format(device_path, pc_path))

    def push(self, pc_path=None, device_path=None):
        self.util.adb('push "{}" "{}"'.format(pc_path, device_path))

    def click(self, x, y):
        self.util.shell('input tap {} {}'.format(x, y))

    def long_click(self, x, y, duration=''):
        """
        长按
        :param x: x 坐标
        :param y: y 坐标
        :param duration: 长按的时间（ms）
        :return:
        """
        self.util.shell('input touchscreen swipe {} {} {} {} {}'.format(x, y, x, y, duration))

    def start(self, pkg):
        """
        使用monkey，只需给出包名即可启动一个应用
        :param pkg:
        :return:
        """
        self.util.shell('monkey -p {} 1'.format(pkg))

    def stop(self, pkg):
        self.util.shell('am force-stop {}'.format(pkg))

    def input(self, text):
        self.util.shell('input text "{}"'.format(text.replace('&', '\&')))

    def back(self, times=1):
        while times:
            self.util.shell('input keyevent 4')
            times -= 1

    def home(self):
        self.util.shell('input keyevent 3')

    def enter(self, times=1):
        while times:
            self.util.shell('input keyevent 66')
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

        self.util.shell('input swipe %s %s %s %s %s' % (str(start_x), str(start_y), str(end_x), str(end_y), str(duration)))

    def clear(self, pkg):
        """
        重置应用
        :param pkg:
        :return:
        """
        self.util.shell('pm clear {}'.format(pkg))

    def wake_up(self):
        """
        点亮屏幕
        :return:
        """
        self.util.shell('input keyevent KEYCODE_WAKEUP')

    def unlock(self):
        """
        解锁屏幕
        :return:
        """
        self.util.shell('input keyevent 82')

    def grant(self, pkg, permission):
        """
        给app赋权限，类似 adb shell pm grant [PACKAGE_NAME] android.permission.PACKAGE_USAGE_STATS
        :return:
        """
        self.util.shell('pm grant {} {}'.format(pkg, permission))

    def install(self, apk_path, with_g=True, with_r=False, user=None):
        """
        安装包
        :param apk_path:
        :param with_g: -g 在一些设备上可以自动授权，默认 true
        :param with_r: -r 覆盖安装，默认 false
        :param user:
        :return:
        """
        arg = 'install'
        if user:
            arg = arg + ' -user {}'.format(user)
        if with_g:
            arg = arg + ' -g'
        if with_r:
            arg = arg + ' -r'
        self.util.adb('{} "{}"'.format(arg, apk_path))

    def uninstall(self, pkg):
        """
        卸载包
        :param pkg:
        :return:
        """
        self.util.adb('uninstall {}'.format(pkg))

    def get_name(self, remove_blank=False):
        name = self.util.shell('getprop ro.config.marketing_name').strip()
        if not name:
            name = self.util.shell('getprop ro.product.nickname').strip()
        if remove_blank:
            name = name.replace(' ', '')
        return name

    def switch_user(self, user_id, wait_time=5):
        self.util.shell('am switch-user {}'.format(user_id))
        time.sleep(wait_time)
