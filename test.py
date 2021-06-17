# coding = utf-8
import logging
import os
import sys
import time
import unittest
from exceptions.assertExcetion import AssertExcetion
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from utils.action import Action
from utils.http import Http
from utils.menu import Menu
from utils.mail import Mail
from HwTestReport import HTMLTestReport as HTMLTestRunner
from utils.parametrized_test_case import ParametrizedTestCase
from utils.test_config import TestConfig, getFileName
# from HTMLTestRunner import HTMLTestRunner
from utils.util import Util


def main():
    global proxy_client, proxy_server
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    log_filename = 'logs/test_' + time.strftime("%Y%m%d",
                                                time.localtime()) + '.log'
    logging.basicConfig(filename=log_filename,
                        level=logging.INFO,
                        format=LOG_FORMAT)

    # 当前脚本所在目录路径
    path = os.path.dirname(os.path.realpath(__file__))

    test_config = TestConfig(path)

    if len(sys.argv) > 1:
        param_type = sys.argv[1]
        # 使用命令显示目录下文件
        if 'ls' == param_type:
            files = getFileName(path + '/config/')
            print(Util.pretty(files))
            return
        elif '-f' == param_type:  # 使用文件路径方式调用测试用例
            if len(sys.argv) < 3:
                print('请输入测试用例配置文件路径(绝对路径)')
                return
            else:
                test_case_path = sys.argv[2]
                report_name = '使用配置文件自动化测试'
                if os.path.exists(test_case_path):
                    print('测试用例文件路径为：' + test_case_path)
                else:
                    print('测试用例文件不存在')
                    return
        else:  # 直接传入测试用例名称
            report_name = param_type
    else:
        report_name = 'default'

    # 获取测试用例数据
    config = test_config.get_test_case(sys.argv)

    # 是否开启代理
    is_open_proxy = config.get('BROWSER').get('proxy')
    if is_open_proxy:
        from browsermobproxy import Server
        bmp_path = config.get('BROWSER').get('bmp_path')
        logging.info('开启代理 ' + bmp_path)
        proxy_server = Server(bmp_path)
        proxy_server.start()
        proxy_client = proxy_server.create_proxy()

    # 浏览器类型
    browser_type = config.get('BROWSER').get('type')

    # 是否使用H5测试，并指定移动设备名称
    h5 = config.get('BROWSER').get('H5', False)
    device_name = config.get('BROWSER').get('device_name', 'iPhone 7')

    # 是否开启无头模式
    headless = config.get('BROWSER').get('headless', False)

    if browser_type == 'Firefox':
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        options.page_load_strategy = 'normal'
        if h5:
            user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
            options.set_preference("general.useragent.override", user_agent)

        if is_open_proxy:
            options.add_argument('--proxy-server={0}'.format(
                proxy_client.proxy))
        browser = webdriver.Firefox(options=options)
    elif browser_type == 'Chrome':
        options = ChromeOptions()
        if headless:
            options.add_argument("--window-size=1920,1080")  # 设置浏览器分辨率（窗口大小）
            options.add_argument(
                "--start-maximized")  # 最大化运行（全屏窗口），不设置，获取元素可能会报错
            options.add_argument("--disable-extensions")
            options.add_argument('--no-sandbox')  # 取消沙盒模式，浏览器的安全性会降低
            # 禁用GPU加速，降低资源损耗，only for Windows but not a valid configuration for Linux OS
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')  # 解决资源有限的问题
            options.add_argument('--lang=en_US')
            options.add_argument("--headless")
        options.page_load_strategy = 'normal'
        if h5:
            mobileEmulation = {'deviceName': device_name}
            options.add_experimental_option('mobileEmulation', mobileEmulation)

        if is_open_proxy:
            options.add_argument('--proxy-server={0}'.format(
                proxy_client.proxy))
        browser = webdriver.Chrome(options=options)
    else:
        print('浏览器' + browser_type + ':类型不支持')
        return False

    logging.info('开始使用 ' + browser_type + ' 浏览器进行自动化测试')

    if is_open_proxy:
        proxy_client.new_har("req",
                             options={
                                 'captureHeaders': True,
                                 'captureContent': True
                             })

    if browser_type == 'Firefox' and h5:
        browser.set_window_size(360, 640)
    else:
        browser.maximize_window()
    # 浏览器等待时间
    # browser.implicitly_wait(10)

    url = config.get('WEBSITE').get('url')
    browser.get(url)
    if is_open_proxy:
        Http.logHar(proxy_client.har)

    # 执行配置的TEST对象
    test = config.get('TEST')
    suite = unittest.TestSuite()
    m = Menu()
    for key in test:
        menus = m.getMenuConfig(config, key)
        try:
            if is_open_proxy:
                test_data = [browser, menus, proxy_client]
            else:
                test_data = [browser, menus]
            suite.addTest(
                ParametrizedTestCase.parametrize(Action,
                                                 'test_menu',
                                                 param=test_data))
        except AssertExcetion:
            print(key + " 断言失败")

    # 是否生成报告，默认开启调试模式，不生成报告
    debug = config.get('DEBUG', True)
    if debug:
        runner = unittest.TextTestRunner()
        runner.run(suite)
    else:
        # 报告是否含有截图，DEBUG为False且IMAGE设置为True时生效
        image = config.get('IMAGE', False)
        report_path = path + '/reports/'
        report_file = report_name + "_" + time.strftime(
            "%Y%m%d", time.localtime()) + '.html'
        fp = open(report_path + report_file, 'wb')
        report_title = '你的测试报告'
        report_desc = '使用配置:' + report_name + '生成的测试报告'
        runner = HTMLTestRunner(stream=fp,
                                verbosity=2,
                                images=image,
                                title=report_title,
                                description=report_desc,
                                tester='pystest')
        runner.run(suite)
        fp.close()

    sleep(5)
    browser.quit()

    # send mail or not
    mail = config.get('MAIL')
    if not debug and mail and mail.get('SEND'):
        email_title = report_title
        email_content = report_desc
        smtp = Mail(config.get('MAIL'), report_path)
        smtp.connect()
        smtp.login()
        smtp.send(email_title, email_content, report_file)
        smtp.quit()

    if is_open_proxy:
        proxy_client.close()
        proxy_server.stop()


if __name__ == "__main__":
    main()
