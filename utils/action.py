# coding = utf-8
import importlib
import os
import time
from operator import methodcaller
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from exceptions.assertExcetion import AssertExcetion
from selenium.webdriver.common.action_chains import ActionChains

class Action:
    def __init__(self, browser):
        self.browser = browser

    # 根据菜单路径执行
    def exMenu(self, menus):
        # 操作是否成功
        assert_result = True

        for menu in menus:
            print(time.strftime("%H:%M:%S", time.localtime()) + " " + menu.get('name'))
            if 'operation' in menu.keys():
                for op in menu.get('operation'):
                    self.operation(op.get('type'), op.get('content'), op.get('value'), op.get('index'), op.get('action'), op)
                    sleep(1)

            self.operation(menu.get('type'), menu.get('content'), menu.get('value'), menu.get('index'), menu.get('action'), menu)
            sleep(1)

            # 断言
            if 'assert' in menu.keys():
                try:
                    self.getElement(menu.get('assert').get('type'), menu.get('assert').get('content'), -1)
                except NoSuchElementException:
                    if menu.get('assert').get('assert') == 1:
                        assert_result = False
                        # 处理失败，可能会有弹窗，多等一会
                        sleep(5)
                        # raise AssertExcetion
                else:
                    if menu.get('assert').get('assert') == 0:
                        assert_result = False
                        # raise AssertExcetion
                sleep(1)

            # 延迟（针对弹框）
            # if 'sleep' in menu.keys():
            #     sleep(menu.get('sleep'))

            # 后置操作(关闭弹出页面等)
            if 'after_operation' in menu.keys():
                for op in menu.get('after_operation'):
                    try:
                        self.operation(op.get('type'), op.get('content'), op.get('value'), op.get('index'), op.get('action'))
                        sleep(1)
                    except NoSuchElementException:
                        # 后置操作，找不到元素不做处理
                        pass

            # 断言失败，抛出
            if not assert_result:
                raise AssertExcetion

    # 操作
    def operation(self, type, content, value, index = -1, action = '', config = {}):
        # 打开操作，是click的一种，但是会判断是否已经打开过
        if action == 'open':
            self.click(type, content, index)
            sleep(1)
            open_element = self.getElement(config.get('open').get('type'), config.get('open').get('content'), -1).is_displayed()
            if open_element == False:
                self.click(type, content, index)
        elif action == 'click':
            self.click(type, content, index, config)
        elif action == 'moveToClick':
            self.moveToClick(type, content, index, config)
        elif action == 'sendKeys':
            self.sendKeys(type, content, value, index, config)
        elif action == 'modifyKeys':
            self.sendKeys(type, content, value, index, config, True)
        elif action == 'sendListKeys':
            self.sendListKeys(type, content, value, index, config, True)
        elif 'select' in action:
            self.select(type, content, index, action)

    # 点击操作
    def click(self, type, content, index = -1, config = {}):
        element = self.getElement(type, content, index, config)
        if 'javascript' in config.keys():
            javascript = config.get('javascript')
            params = javascript.split('.')
            if params[0] == 'setAttribute':
                self.browser.execute_script("arguments[0].setAttribute(arguments[1], arguments[2])", element, params[1], params[2])

        element.click()

    # 移动并点击操作
    def moveToClick(self, type, content, index = -1, config = {}):
        element = self.getElement(type, content, index, config)
        if 'javascript' in config.keys():
            javascript = config.get('javascript')
            params = javascript.split('.')
            if params[0] == 'setAttribute':
                self.browser.execute_script("arguments[0].setAttribute(arguments[1], arguments[2])", element, params[1], params[2])

        ActionChains(self.browser).move_to_element(element).click().perform()

    # 默认填写值
    def sendKeys(self, type, content, value, index = -1, config = {}, modify = False):
        element = self.getElement(type, content, index)
        self.writeKey(element, value, modify)

    # 给列表填写值
    def sendListKeys(self, type, content, value, index = -1, config = {}, modify = False):
        elements = self.getElement(type, content, index, config)
        for element in elements:
            self.writeKey(element, value, modify)

    # 写值到元素里
    def writeKey(self, element, value, modify = False):
        if 'pkgpath' in value:
            callbacks = value.split(':')
            pkg = callbacks[1]
            func = callbacks[2]

            try:
                params = callbacks[3]
            except IndexError:
                params = ''

            klass = self.myImport(pkg)
            if params != '':
                value = methodcaller(func, params)(klass())
            else:
                value = methodcaller(func)(klass())

        # 清空旧值
        if modify:
            element.clear()
            sleep(0.5)

        element.send_keys(value)

    # 选择元素
    def select(self, type, content, index, action):
        params = action.split('.')
        elements = self.getElement(type, content, index)
        for element in elements:
            is_show = element.is_displayed()
            if is_show == True:
                element.find_elements(self.getType(params[1]), params[2])[int(params[3])].click()

    # 获取元素
    def getElement(self, type, content, index, config = {}, element = {}):
        msg = 'type:' + type + ',index:' + str(index) + ',content:' + content
        if (config and 'contents' in config.keys()):
            contents = config.get('contents')
            for op in contents:
                element = self.getElement(op.get('type'), op.get('content'), op.get('index'), {}, element)
        else:
            if element:
                if index >= 0:
                    try:
                        result = element.find_elements(self.getType(type), content)
                        return result[index]
                    except NoSuchElementException:
                        print(msg+',元素不存在')
                    except IndexError:
                        print(msg+',元素不存在或超出list限制')
                        os._exit(0)
                elif index == -2:
                    return element.find_elements(self.getType(type), content)
                else:
                    return element.find_element(self.getType(type), content)
            else:
                if index >= 0:
                    try:
                        result = self.browser.find_elements(self.getType(type), content)
                        return result[index]
                    except NoSuchElementException:
                        print(msg+',元素不存在')
                    except IndexError:
                        print(msg+',元素不存在或超出list限制')
                        os._exit(0)
                elif index == -2:
                    return self.browser.find_elements(self.getType(type), content)
                else:
                    return self.browser.find_element(self.getType(type), content)

        return element

    def getType(self, type):
        if type == 'id':
            return By.ID
        elif type == 'class name':
            return By.CLASS_NAME
        elif type == 'xpath':
            return By.XPATH
        elif type == 'link text':
            return By.LINK_TEXT
        elif type == 'partial link text':
            return By.PARTIAL_LINK_TEXT
        elif type == 'name':
            return By.NAME
        elif type == 'tag name':
            return By.TAG_NAME
        elif type == 'css selector':
            return By.CSS_SELECTOR

    def myImport(self, pkgpath):
        components = pkgpath.split('.')
        mod = __import__(components[0]+'.'+components[1], fromlist=[components[2]])
        klass = getattr(mod, components[2])

        return klass
