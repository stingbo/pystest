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
        self.imgs = []
        menus = self.param[1]
        try:
            proxy = self.param[2]
        except IndexError:
            proxy = {}

        for menu in menus:
            print(
                time.strftime("%H:%M:%S", time.localtime()) + " " +
                menu.get('name'))

            # 始终获得当前最后的窗口，所以多要多次使用
            search_windows = self.browser.current_window_handle
            for handle in self.browser.window_handles:
                if handle != search_windows:
                    self.browser.switch_to.window(handle)

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

            self.get_screenshot()
            if 'operation' in menu.keys():
                for op in menu.get('operation'):
                    self.operation(op)

            self.operation(menu)

            # http请求监听
            if proxy and 'listener' in menu.keys():
                proxy.wait_for_traffic_to_stop(1, 1000)
                http = Http()
                http.listener(proxy.har, menu.get('listener'))

            failures = []
            if 'assert' in menu:
                checks = menu['assert']
                if not isinstance(checks, list):
                    checks = [checks]
                for index, check in enumerate(checks, start=1):
                    failure = self.check_assertion(check)
                    if failure:
                        failures.append(f'#{index}: {failure}')
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
            if failures:
                raise AssertExcetion(f"{menu['name']}\n" + '\n'.join(failures))

    def check_assertion(self, config):
        if not isinstance(config, dict):
            return 'assert 配置必须是映射'

        check = config.get('check')
        legacy = 'check' not in config
        if legacy:
            expected_presence = config.get('assert')
            if expected_presence not in (0, 1):
                return '旧版 assert 配置需要指定 0 或 1'
            check = 'exists' if expected_presence == 1 else 'not_exists'

        expected = config.get('expected')
        if check in ('text_equals', 'url_ends_with') and not isinstance(expected, str):
            return f'{check} 需要字符串 expected'

        if check == 'url_ends_with':
            actual = self.browser.current_url
            if not actual.endswith(expected):
                return f'{check}: 当前网址 {actual!r} 应以 {expected!r} 结尾'
            return None

        if check not in ('exists', 'not_exists', 'text_equals'):
            return f'不支持的断言类型 {check!r}'

        locator_type = config.get('type')
        locator_content = config.get('content')
        if not locator_type or not locator_content:
            return f'{check} 需要指定元素定位方式 type 和定位值 content'

        locator = f'{locator_type}={locator_content!r}'
        try:
            element = self.el.get(locator_type, locator_content, -1)
        except NoSuchElementException:
            if check == 'not_exists':
                return None
            if legacy:
                # 保留旧版断言失败后等待弹窗的行为
                sleep(5)
            return f'{check}: 找不到元素 {locator}'

        if check == 'not_exists':
            return f'{check}: 找到了不应存在的元素 {locator}'
        if check == 'text_equals':
            actual = element.text
            if actual != expected:
                return f'{check}: 元素 {locator} 的文本为 {actual!r}，期望 {expected!r}'
        return None

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
        self.get_screenshot()

    def get_screenshot(self):
        self.imgs.append(self.browser.get_screenshot_as_base64())
