# adbui
adbui 所有的功能都是通过 adb 命令，adbui 的特色是可以通过 xpath，ocr 获取 ui 元素。

## 安装
$ pip install adbui

## 要求
在命令中可以使用 adb 命令，即adb已经配置到环境变量

## 说明
- adbui 当前还在完善，bug 和建议请直接在 github 反馈
- 主要在 win7，python3 环境使用，其他环境可能有问题
- 依赖的库：lxml 解析 xml，requests 发 ocr 请求，pillow 图片处理


## 使用
    from adbui import Device

    d = Devece('123abc')  # 手机的sn号，如果只有一个手机可以不写


### adbui 大概可以分为 3 个部分
**util 是基础，主要负责执行完整的命令**
  - **cmd** 用来执行系统命令，如 d.util.cmd('adb -s 123abc reboot')
  - **adb** 用来执行 adb 命令，如 d.util.adb('install xxx.apk')
  - **shll** 用来执行 shell 命令，如 d.util.shell('pm clear com.tencent.mtt')

**adb_ext 是对常用adb命令的封装，下面列出部分操作（可在 adbui/adb_ext.py 文件自行增加需要的操作）**
  - **screenshot** 截屏  d.adb_ext.screenshot() # 截图保存到系统临时目录
  - **click** 点击一个 point d.adb_ext.click((10, 32))
  - **input** 输入文本 d.adb_ext.input('adbui')
  - **back** 发出 back 指令 d.adb_ext.back()


**get_ui 就是特色功能，可以通过多种方式获取 UI**
  - **by attr** 通过在 uiautomator 里面看到的属性来获取
       ```python
        ui = d.get_ui_by_attr(text='设置', desc='设置')  # 支持多个属性同时查找

        ui = d.get_ui_by_attr(text='设', is_contains=True)  # 支持模糊查找

        ui = d.get_ui_by_attr(text='设置', is_update=False)  # 如果需要在一个界面上获取多个 UI， 再次查找时可以设置不更新xml文件和截图，节省时间

        ui = d.get_ui_by_attr(class_='android.widget.TextView')  # class 在 python 中是关键字，因此使用 class_ 代替

        ui = d.get_ui_by_attr(desc='fffffff')  # 如果没有找到，返回 None;如果找到多个返回第一个

        ui = d.get_uis_by_attr(desc='fffffff')  # 如果是 get uis 没有找到，返回空的 list
  - **by xpath** 使用 xpath 来获取

  - **by ocr** 使用腾讯的OCR技术来获取
