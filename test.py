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
from utils.parametrized_test_case import ParametrizedTestCase
from utils.test_config import TestConfig, getFileName
from HTMLTestRunner import HTMLTestRunner
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
        report_name = sys.argv[1]
        if 'ls' == sys.argv[1]:
            files = getFileName(path + '/config/')
            print(Util.pretty(files))
            return
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

    browser_type = config.get('BROWSER').get('type')
    h5 = config.get('BROWSER').get('h5', False)
    device_name = config.get('BROWSER').get('device_name', 'iPhone 7')
    if browser_type == 'Firefox':
        options = FirefoxOptions()
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

    # 是否生成报告
    debug = config.get('DEBUG')
    if debug:
        runner = unittest.TextTestRunner()
        runner.run(suite)
    else:
        report_path = path + '/reports/'
        report_file = report_name + "_" + time.strftime(
            "%Y%m%d", time.localtime()) + '.html'
        fp = open(report_path + report_file, 'w', encoding='utf-8')
        report_title = '你的测试报告'
        report_desc = '使用配置:' + report_name + '生成的测试报告'
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp,
                                               title=report_title,
                                               description=report_desc)
        runner.run(suite)
        fp.close()

    sleep(5)
    browser.quit()

    if is_open_proxy:
        proxy_client.close()
        proxy_server.stop()


if __name__ == "__main__":
    main()
