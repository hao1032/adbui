from adbui import Device

d = Device()
d.init_ocr()
ui = d.get_ui_by_ocr(text='声音')
print(ui)
ui.click()