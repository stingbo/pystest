# coding = utf-8
import logging
import yaml
import os
import sys
import time
import unittest
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from exceptions.assertExcetion import AssertExcetion
from utils.action import Action
from utils.util import Util
from utils.menu import Menu
from utils.ParametrizedTestCase import ParametrizedTestCase
from HTMLTestRunner import HTMLTestRunner


def main():
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logfilename = 'logs/test_' + time.strftime("%Y%m%d",
                                               time.localtime()) + '.log'
    logging.basicConfig(filename=logfilename,
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
        testfilename = sys.argv[1]
        config_file = "/config/" + testfilename + ".yaml"
    else:
        testfilename = 'default'
        config_file = "/config/" + testfilename + '.yaml'

    # yaml配置文件是否存在
    config_file_path = curpath + config_file
    if not os.path.isfile(config_file_path):
        print("配置文件不存在 " + config_file_path)
        return 1

    f = open(config_file_path, 'r', encoding='utf-8')
    config = yaml.safe_load(f.read())

    # 合并配置
    config = Util.recursionMergeTwoDict(global_config, config)

    browser_type = config.get('BROWSER').get('type')
    if browser_type == 'Firefox':
        options = FirefoxOptions()
        options.page_load_strategy = 'normal'
        browser = webdriver.Firefox(options=options)
    elif browser_type == 'Chrome':
        options = ChromeOptions()
        options.page_load_strategy = 'normal'
        browser = webdriver.Chrome(options=options)
    else:
        print('浏览器' + browser_type + ':类型不支持')
        os._exit(0)

    logging.info('开始使用 ' + browser_type + ' 浏览器进行自动化测试')

    browser.maximize_window()
    # 浏览器等待时间
    # browser.implicitly_wait(10)

    url = config.get('WEBSITE').get('url')
    browser.get(url)

    # 执行配置的TEST对象
    test = config.get('TEST')
    suite = unittest.TestSuite()
    for key in test:
        menus = Menu.getMenuConfig(config, key)
        try:
            testData = [browser, menus]
            suite.addTest(
                ParametrizedTestCase.parametrize(Action,
                                                 'test_menu',
                                                 param=testData))
        except AssertExcetion:
            print(key + " 断言失败")

    reportfilename = 'reports/' + testfilename + "_" + time.strftime(
        "%Y%m%d", time.localtime()) + '.html'
    fp = open(reportfilename, 'w', encoding='utf-8')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp,
                                           title='你的测试报告',
                                           description='使用配置文件:' +
                                           config_file_path + '生成的测试报告')
    runner.run(suite)
    fp.close()

    sleep(5)
    browser.quit()


if __name__ == "__main__":
    main()
