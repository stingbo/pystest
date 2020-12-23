# coding = utf-8
import time
from selenium.common.exceptions import NoSuchElementException
from exceptions.assertExcetion import AssertExcetion
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from utils.element import Element
from utils.http import Http
from utils.javascript import Javascript
from utils.operation import Operation
from utils.parametrized_test_case import ParametrizedTestCase
from utils.wait import WaitDisappear


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
            if 'iframe' not in menu.keys():
                self.browser.switch_to.default_content()
            elif 'iframe' in menu.keys() and menu.get('iframe') != 'none':
                self.browser.switch_to.frame(menu.get('iframe'))
            else:
                pass

            # 是否等待页面加载
            if 'wait' in menu.keys():
                wait = WebDriverWait(self.browser, 10, poll_frequency=1)
                locator = (menu.get('wait').get('type'),
                           menu.get('wait').get('content'))
                wait.until(EC.presence_of_element_located(locator))
                # wait.until(EC.element_to_be_clickable(locator))
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
        # 查找元素
        element = self.el.get(type, content, index, config)

        # 执行js
        if 'javascript' in config.keys():
            js_code = config.get('javascript')
            js = Javascript(self.browser, element)
            js.exjavascript(js_code)

        # 执行具体动作
        op = Operation(self.browser, element)
        op.operation(config)
