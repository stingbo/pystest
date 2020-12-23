# coding = utf-8
from operator import methodcaller
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
from utils.element import getType


# 导入包
def pys_import(pkg):
    components = pkg.split('.')
    mod = __import__(components[0] + '.' + components[1],
                     fromlist=[components[2]])
    klass = getattr(mod, components[2])

    return klass


class Operation:
    def __init__(self, browser, element):
        self.browser = browser
        self.element = element

    def operation(self, config):
        if 'action' not in config.keys():
            return

        action = config.get('action', '')
        if not action:
            return

        if action == 'open':
            self.open(config)
        elif action == 'click':
            self.click()
        elif action == 'clickList':
            self.clickList()
        elif action == 'moveToClick':
            self.moveToClick()
        elif action == 'jsclick':
            self.jsclick()
        elif action == 'sendKeys':
            self.sendKeys(config.get('value'))
        elif action == 'modifyKeys':
            self.sendKeys(config.get('value'), True)
        elif action == 'sendListKeys':
            self.sendListKeys(config.get('value'), True)
        elif action == 'upload':
            self.upload(config.get('value'))
        elif 'select' in action:
            self.select(action)
        else:
            # print('无操作'+action)
            pass

    # 打开操作，是click的一种，但是会判断是否已经打开过
    def open(self, config):
        if config.get('open').get('class') not in self.element.get_attribute(
                "class"):
            self.click()

    # 点击操作
    def click(self):
        self.element.click()

    # js点击操作
    def jsclick(self):
        self.browser.execute_script('arguments[0].click()', self.element)

    # 给列表填写值
    def clickList(self):
        for el in self.element:
            el.click()

    # 移动并点击操作
    def moveToClick(self):
        ActionChains(self.browser).click(self.element).perform()

    # 默认填写值
    def sendKeys(self, value, modify=False):
        self.writeKey(self.element, value, modify)

    # 给列表填写值
    def sendListKeys(self, value, modify=False):
        for el in self.element:
            self.writeKey(el, value, modify)

    # 上传文件
    def upload(self, value):
        # filepath = os.getcwd() + value
        # print(filepath)
        # self.writeKey(element, filepath)
        self.writeKey(self.element, value)

    # 写值到元素里
    def writeKey(self, element, value, modify=False):
        if 'pkgpath' in value:
            callbacks = value.split(':')
            pkg = callbacks[1]
            func = callbacks[2]

            try:
                param = callbacks[3]
                if ',' in param:
                    params = param.split(',')
                else:
                    params = [param]
            except IndexError:
                params = []

            klass = pys_import(pkg)
            if params:
                value = methodcaller(func, params)(klass())
            else:
                value = methodcaller(func)(klass())

        # 清空旧值
        if modify:
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.DELETE)
            # element.clear()
            sleep(0.5)

        element.send_keys(value)

    # 选择元素
    def select(self, action):
        params = action.split('.')
        for el in self.element:
            is_show = el.is_displayed()
            if is_show:
                el.find_elements(getType(params[1]),
                                 params[2])[int(params[3])].click()
