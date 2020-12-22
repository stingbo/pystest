# coding = utf-8
# import os
import time
from operator import methodcaller
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from selenium.webdriver.common.keys import Keys
from exceptions.assertExcetion import AssertExcetion
from selenium.webdriver.common.action_chains import ActionChains
from utils.ParametrizedTestCase import ParametrizedTestCase
from utils.http import Http
from utils.element import Element
from utils.javascript import Javascript
from utils.wait import WaitDisappear
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait  # 等待页面加载某些元素


class Action(ParametrizedTestCase):
    # 根据菜单路径执行
    def test_menu(self):
        self.browser = self.param[0]
        self.el = Element(self.param[0])
        menus = self.param[1]
        try:
            proxy = self.param[2]
        except IndexError:
            proxy = {}

        # 操作是否成功
        assert_result = True

        for menu in menus:
            print(
                time.strftime("%H:%M:%S", time.localtime()) + " " +
                menu.get('name'))

            # 是否等待页面消失
            if 'wait_disappear' in menu.keys():
                wait = WebDriverWait(self.browser, 10, poll_frequency=1)
                my_wait = WaitDisappear(menu.get('wait_disappear'))
                wait.until(my_wait)

            # 切换iframe
            if 'iframe' in menu.keys():
                iframe = menu.get('iframe', '')
                if iframe and iframe != 'none':
                    self.browser.switch_to.frame(menu.get('iframe'))
                else:
                    pass
            else:
                self.browser.switch_to.default_content()

            # 是否等待页面加载
            if 'wait' in menu.keys():
                wait = WebDriverWait(self.browser, 10, poll_frequency=1)
                locator = (menu.get('wait').get('type'),
                           menu.get('wait').get('content'))
                # wait.until(EC.presence_of_element_located(locator))
                wait.until(EC.element_to_be_clickable(locator))
                # wait.until(EC.visibility_of_element_located(locator))

            # http请求监听
            if proxy and 'listener' in menu.keys():
                proxy.new_har("test",
                              options={
                                  'captureHeaders': True,
                                  'captureContent': True,
                                  'captureBinaryContent': True
                              })

            if 'operation' in menu.keys():
                for op in menu.get('operation'):
                    self.operation(op)

            self.operation(menu)

            # http请求监听
            if proxy and 'listener' in menu.keys():
                proxy.wait_for_traffic_to_stop(1, 1000)
                http = Http()
                http.listener(proxy.har, menu.get('listener'))

            # 断言
            if 'assert' in menu.keys():
                try:
                    self.el.get(
                        menu.get('assert').get('type'),
                        menu.get('assert').get('content'), -1)
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
                        self.operation(op)
                        sleep(1)
                    except NoSuchElementException:
                        # 后置操作，找不到元素不做处理
                        pass

            # 断言失败，抛出
            if not assert_result:
                raise AssertExcetion

    # 操作
    def operation(self, config):
        if 'wait_time' in config.keys() and (
                isinstance(config.get('wait_time'), int)
                or isinstance(config.get('wait_time'),
                              float)) and config.get('wait_time') > 0:
            sleep(config.get('wait_time'))
        else:
            sleep(1)

        # content与contents都不存在，则后续流程不执行
        if ('content' not in config.keys() or not config.get('content')
                or config.get('content')
                == 'none') and ('contents' not in config.keys()
                                or not config.get('contents')
                                or config.get('contents') == 'none'):
            return

        type = config.get('type')
        content = config.get('content')
        index = config.get('index')
        value = config.get('value')
        action = config.get('action')
        element = self.el.get(type, content, index, config)
        if 'javascript' in config.keys():
            js_code = config.get('javascript')
            js = Javascript(self.browser, element)
            js.exjavascript(js_code)

        if action == 'open':
            self.open(element, config)
        elif action == 'click':
            self.click(element)
        elif action == 'clickList':
            self.clickList(element)
        elif action == 'moveToClick':
            self.moveToClick(element)
        elif action == 'jsclick':
            self.jsclick(element)
        elif action == 'sendKeys':
            self.sendKeys(element, value)
        elif action == 'modifyKeys':
            self.sendKeys(element, value, True)
        elif action == 'sendListKeys':
            self.sendListKeys(element, value, True)
        elif action == 'upload':
            self.upload(element, value)
        elif 'select' in action:
            self.select(element, action)
        else:
            # print('无操作'+action)
            pass

    # 打开操作，是click的一种，但是会判断是否已经打开过
    def open(self, element, config):
        if config.get('open').get('class') not in element.get_attribute(
                "class"):
            self.click(element)

    # 点击操作
    def click(self, element):
        element.click()

    # js点击操作
    def jsclick(self, element):
        self.browser.execute_script('arguments[0].click()', element)

    # 给列表填写值
    def clickList(self, elements):
        for element in elements:
            element.click()

    # 移动并点击操作
    def moveToClick(self, element):
        ActionChains(self.browser).move_to_element(element).click().perform()

    # 默认填写值
    def sendKeys(self, element, value, modify=False):
        self.writeKey(element, value, modify)

    # 给列表填写值
    def sendListKeys(self, elements, value, modify=False):
        for element in elements:
            self.writeKey(element, value, modify)

    # 上传文件
    def upload(self, element, value):
        # filepath = os.getcwd() + value
        # print(filepath)
        # self.writeKey(element, filepath)
        self.writeKey(element, value)

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

            klass = self.myImport(pkg)
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
    def select(self, elements, action):
        params = action.split('.')
        for element in elements:
            is_show = element.is_displayed()
            if is_show:
                element.find_elements(self.el.getType(params[1]),
                                      params[2])[int(params[3])].click()

    # 导入包
    def myImport(self, pkgpath):
        components = pkgpath.split('.')
        mod = __import__(components[0] + '.' + components[1],
                         fromlist=[components[2]])
        klass = getattr(mod, components[2])

        return klass
