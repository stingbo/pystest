# coding = utf-8
import logging
import os
import sys
import time
import traceback
import unittest
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
from itertools import repeat
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from utils.action import Action
from utils.http import Http
from utils.menu import Menu
from utils.mail import Mail
from HwTestReport import HTMLTestReport as HTMLTestRunner
from utils.test_config import TestConfig, getFileName
from utils.util import Util


def configure_logging(log_name):
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    log_filename = os.path.join('logs', log_name + '.log')
    logging.basicConfig(filename=log_filename,
                        level=logging.INFO,
                        format=LOG_FORMAT)


def create_browser(config, proxy_client):
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

        if proxy_client is not None:
            options.add_argument('--proxy-server={0}'.format(
                proxy_client.proxy))
        browser = webdriver.Firefox(options=options)
    elif browser_type == 'Chrome':
        options = ChromeOptions()
        if headless:
            options.add_argument('--no-sandbox')  # 取消沙盒模式，浏览器的安全性会降低
            options.add_argument("--window-size=1920,1080")  # 设置浏览器分辨率（窗口大小）
            options.add_argument(
                "--start-maximized")  # 最大化运行（全屏窗口），不设置，获取元素可能会报错
            options.add_argument("--disable-extensions")
            # 禁用GPU加速，降低资源损耗，only for Windows but not a valid configuration for Linux OS
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')  # 解决资源有限的问题
            options.add_argument('--lang=en_US')
            options.add_argument("--headless")
        options.page_load_strategy = 'normal'
        if h5:
            mobileEmulation = {'deviceName': device_name}
            options.add_experimental_option('mobileEmulation', mobileEmulation)

        if proxy_client is not None:
            options.add_argument('--proxy-server={0}'.format(
                proxy_client.proxy))
        browser = webdriver.Chrome(options=options)
    else:
        raise ValueError(f'不支持的浏览器类型 {browser_type!r}')

    return browser


def open_start_page(browser, config, proxy_client):
    browser_config = config['BROWSER']
    logging.info('开始使用 %s 浏览器进行自动化测试', browser_config['type'])

    if proxy_client is not None:
        proxy_client.new_har("req",
                             options={
                                 'captureHeaders': True,
                                 'captureContent': True
                             })

    if browser_config['type'] == 'Firefox' and browser_config.get('H5'):
        browser.set_window_size(360, 640)
    else:
        browser.maximize_window()

    url = config.get('WEBSITE').get('url')
    browser.get(url)
    if proxy_client is not None:
        Http.logHar(proxy_client.har)


class GroupAction(Action):
    def __init__(self, key, test_data):
        super().__init__('test_menu', param=test_data)
        self.key = key

    def shortDescription(self):
        return self.key


class DependentSuite(unittest.TestSuite):
    def run(self, result, debug=False):
        failed_key = None
        for test in self:
            if failed_key is not None:
                result.startTest(test)
                try:
                    result.addSkip(test, f'前置用例 {failed_key} 未通过')
                finally:
                    result.stopTest(test)
                continue

            issues_before = len(result.failures) + len(result.errors) + len(result.skipped)
            test(result)
            issues_after = len(result.failures) + len(result.errors) + len(result.skipped)
            if issues_after > issues_before:
                failed_key = test.key
        return result


def run_cases(config, cases, report_file, proxy_server, grouped=False):
    with ExitStack() as resources:
        proxy_client = None
        if proxy_server is not None:
            proxy_client = proxy_server.create_proxy()
            resources.callback(proxy_client.close)

        browser = create_browser(config, proxy_client)
        resources.callback(browser.quit)
        open_start_page(browser, config, proxy_client)

        suite = DependentSuite() if grouped else unittest.TestSuite()
        menu = Menu()
        for key in cases:
            test_data = [browser, menu.getMenuConfig(config, key)]
            if proxy_client is not None:
                test_data.append(proxy_client)
            test = GroupAction(key, test_data) if grouped else Action('test_menu', param=test_data)
            suite.addTest(test)

        if report_file is None:
            result = unittest.TextTestRunner(verbosity=2 if grouped else 1).run(suite)
        else:
            with open(report_file, 'wb') as stream:
                runner = HTMLTestRunner(
                    stream=stream, verbosity=2, images=config.get('IMAGE', False),
                    title='你的测试报告',
                    description=f'使用配置生成的测试报告：{os.path.basename(report_file)}',
                    tester='pystest')
                result = runner.run(suite)

        if not grouped:
            sleep(5)
        return result


def run_group(config, proxy_address, job):
    _, cases, report_file = job
    try:
        proxy_server = None
        if proxy_address is not None:
            from browsermobproxy.server import RemoteServer
            proxy_server = RemoteServer(*proxy_address)
        result = run_cases(config, cases, report_file, proxy_server, grouped=True)
    except Exception:
        # 组的浏览器启动或配置失败时，仍等待其他组完成。
        return False, 0, [], traceback.format_exc()

    skipped = [(test.key, reason) for test, reason in result.skipped]
    return result.wasSuccessful(), result.testsRun - len(skipped), skipped, None


def configure_worker_logging():
    configure_logging(f'test_{time.strftime("%Y%m%d")}_worker_{os.getpid()}')


def grouped_jobs(config, report_path, report_name):
    groups = config['TEST_GROUPS']
    if not isinstance(groups, dict) or not groups:
        raise ValueError('TEST_GROUPS 必须是非空映射')
    workers = config.get('PARALLEL_WORKERS', 2)
    if type(workers) is not int or workers < 1:
        raise ValueError('PARALLEL_WORKERS 必须是正整数')
    for name, cases in groups.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError('TEST_GROUPS 的组名必须是非空字符串')
        if not isinstance(cases, list) or not cases or any(
                not isinstance(key, str) or not key.strip() for key in cases):
            raise ValueError(f'TEST_GROUPS 中 {name!r} 必须是非空用例名称列表')

    jobs = []
    for index, (name, cases) in enumerate(groups.items(), start=1):
        group_report = None
        if report_path is not None:
            group_report = os.path.join(report_path, f'{report_name}_group_{index}.html')
        jobs.append((name, cases, group_report))
    # Windows 的 ProcessPoolExecutor 最多支持 61 个工作进程。
    return min(workers, len(jobs), 61 if os.name == 'nt' else len(jobs)), jobs


def main():
    configure_logging('test_' + time.strftime("%Y%m%d"))
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

    debug = config.get('DEBUG', True)
    report_path = None if debug else os.path.join(path, 'reports')
    report_name = report_name + '_' + time.strftime("%Y%m%d")
    grouped = 'TEST_GROUPS' in config
    if grouped:
        workers, jobs = grouped_jobs(config, report_path, report_name)

    reports = []
    successful = True
    with ExitStack() as resources:
        proxy_server = None
        if config['BROWSER'].get('proxy'):
            from browsermobproxy import Server
            bmp_path = config['BROWSER'].get('bmp_path')
            logging.info('开启代理 %s', bmp_path)
            proxy_server = Server(bmp_path)
            proxy_server.start()
            resources.callback(proxy_server.stop)

        if not grouped or config.get('TEST'):
            report_file = None if debug else os.path.join(report_path, report_name + '.html')
            result = run_cases(config, config['TEST'], report_file, proxy_server)
            successful = result.wasSuccessful()
            if report_file is not None:
                reports.append(report_file)

        if grouped:
            proxy_address = None if proxy_server is None else (proxy_server.host, proxy_server.port)
            # HTMLTestReport 在执行时重定向整个进程的 stdout/stderr。
            with ProcessPoolExecutor(max_workers=workers,
                                     initializer=configure_worker_logging) as executor:
                results = executor.map(run_group, repeat(config), repeat(proxy_address), jobs)
                for (name, _, report_file), (passed, executed, skipped, error) in zip(jobs, results):
                    successful = successful and passed
                    status = '通过' if passed else '未通过'
                    print(f'[{name}] {status}，执行 {executed} 条，跳过 {len(skipped)} 条')
                    for key, reason in skipped:
                        print(f'  跳过 {key}：{reason}')
                    if error:
                        print(error, file=sys.stderr)
                    elif report_file is not None:
                        reports.append(report_file)
                        print(f'  报告：{report_file}')

    mail = config.get('MAIL')
    if reports and mail and mail.get('SEND'):
        smtp = Mail(mail, report_path)
        smtp.connect()
        try:
            smtp.login()
            for report_file in reports:
                smtp.send('你的测试报告', f'测试报告：{os.path.basename(report_file)}',
                          os.path.basename(report_file))
        finally:
            smtp.quit()

    if grouped and not successful:
        return 1


if __name__ == "__main__":
    sys.exit(main())
