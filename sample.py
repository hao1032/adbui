from adbui import Device, Util
import time
import platform

d = Device()

ui = d.get_ui_by_ocr('阅读')
print(ui)

ui = d.get_ui_by_attr(text='设置', is_contains=True)
ui.click()

time.sleep(1)
ui = d.get_ui_by_ocr(text='显示')
ui.click()
