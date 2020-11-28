# coding = utf-8
import logging
import yaml
import os
import sys
import time
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from exceptions.assertExcetion import AssertExcetion
from browsermobproxy import Server
from utils.action import Action
from utils.har import Log
from utils.util import Util
from utils.menu import Menu

def main():
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logfilename = 'logs/test_' + time.strftime("%Y%m%d", time.localtime()) + '.log'
    logging.basicConfig(filename=logfilename, level=logging.INFO, format=LOG_FORMAT)

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
        config_file = "/config/" + sys.argv[1] + ".yaml"
    else:
        config_file = "/config/default.yaml"

    # yaml配置文件是否存在
    config_file_path = curpath + config_file
    if not os.path.isfile(config_file_path):
        print("配置文件不存在 " + config_file_path)
        return 1

    f = open(config_file_path, 'r', encoding='utf-8')
    config = yaml.safe_load(f.read())

    # 合并配置
    config = Util.recursionMergeTwoDict(global_config, config)

    proxyserver = config.get('BROWSER').get('proxyserver')
    logging.info('开启代理 ' + proxyserver)
    server = Server(proxyserver)
    server.start()
    proxy = server.create_proxy()

    browser_type = config.get('BROWSER').get('type')
    if browser_type == 'Firefox':
        options = FirefoxOptions()
        options.page_load_strategy = 'normal'
        options.add_argument('--proxy-server={0}'.format(proxy.proxy))
        browser = webdriver.Firefox(options=options)
    elif browser_type == 'Chrome':
        options = ChromeOptions()
        options.page_load_strategy = 'normal'
        options.add_argument('--proxy-server={0}'.format(proxy.proxy))
        browser = webdriver.Chrome(options=options)
    else:
        print('浏览器'+browser_type+':类型不支持')
        os._exit(0)

    logging.info('开始使用 ' + browser_type + ' 浏览器进行自动化测试')
    proxy.new_har("req", options={'captureHeaders': True, 'captureContent': True})

    browser.maximize_window()
    # 浏览器等待时间
    browser.implicitly_wait(3)

    url = config.get('WEBSITE').get('url')
    browser.get(url)
    Log.logHar(proxy.har)

    # 初始化操作对象
    action = Action(browser)

    # 执行配置的TEST对象
    test = config.get('TEST')
    for key in test:
        menus = Menu.getMenuConfig(config, key)
        try:
            action.exMenu(menus)
        except AssertExcetion:
            print(key + " 断言失败")

        # 是否等待页面加载 todo
        # if 'wait' in menu_config.keys():
        #     wait = WebDriverWait(browser, 10, 0.5)
        #     locator = (menu_config.get('wait').get('type'), menu_config.get('wait').get('content'))
        #     wait.until(EC.presence_of_element_located(locator))

    sleep(5)
    browser.quit()


if __name__ == "__main__":
    main()
