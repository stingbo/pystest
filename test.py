# coding = utf-8
import logging
import os
import sys
import time
import unittest
import yaml
from exceptions.assertExcetion import AssertExcetion
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from utils.action import Action
from utils.http import Http
from utils.menu import Menu
from utils.parametrized_test_case import ParametrizedTestCase
from utils.util import Util
from HTMLTestRunner import HTMLTestRunner


def main():
    global proxy_client, proxy_server
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    log_filename = 'logs/test_' + time.strftime("%Y%m%d",
                                                time.localtime()) + '.log'
    logging.basicConfig(filename=log_filename,
                        level=logging.INFO,
                        format=LOG_FORMAT)

    # 当前脚本所在目录路径
    curpath = os.path.dirname(os.path.realpath(__file__))

    # 全局config文件
    global_config = {}
    global_config_file_path = curpath + "/config.yaml"
    if os.path.isfile(global_config_file_path):
        gf = open(global_config_file_path, 'r', encoding='utf-8')
        global_config = yaml.safe_load(gf.read())

    # 是否传入配置文件
    if len(sys.argv) > 1:
        test_filename = sys.argv[1]
        config_file = "/config/" + test_filename + ".yaml"
    else:
        test_filename = 'default'
        config_file = "/config/" + test_filename + '.yaml'

    # yaml配置文件是否存在
    config_file_path = curpath + config_file
    if not os.path.isfile(config_file_path):
        print("配置文件不存在 " + config_file_path)
        return 1

    f = open(config_file_path, 'r', encoding='utf-8')
    config = yaml.safe_load(f.read())

    # 合并配置
    config = Util.recursionMergeTwoDict(global_config, config)

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
    if browser_type == 'Firefox':
        options = FirefoxOptions()
        options.page_load_strategy = 'normal'
        if is_open_proxy:
            options.add_argument('--proxy-server={0}'.format(
                proxy_client.proxy))
        browser = webdriver.Firefox(options=options)
    elif browser_type == 'Chrome':
        options = ChromeOptions()
        options.page_load_strategy = 'normal'
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

    report_file_name = 'reports/' + test_filename + "_" + time.strftime(
        "%Y%m%d", time.localtime()) + '.html'
    fp = open(report_file_name, 'w', encoding='utf-8')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp,
                                           title='你的测试报告',
                                           description='使用配置文件:' +
                                           config_file_path + '生成的测试报告')
    runner.run(suite)
    fp.close()

    sleep(5)
    browser.quit()

    if is_open_proxy:
        proxy_client.close()
        proxy_server.stop()


if __name__ == "__main__":
    main()
