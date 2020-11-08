# coding = utf-8

from selenium.webdriver.common.by import By

class BaseInfo:
    def __init__(self, browser, config):
        self.browser = browser
        self.menu = config.get('MENU').get('BASE_INFO')

        # 打开基础档案菜单
        self.browser.find_elements_by_class_name(self.menu.get('icon'))[0].click()

    def companyInfo(self):
        submenu_name = self.menu.get('submenu')[0].get('name') #企业信息
        self.browser.find_element(By.XPATH, "//span[text()='"+submenu_name+"']/..").click()

        return self.browser

    def depot(self):
        submenu_name = self.menu.get('submenu')[3].get('name') #仓库档案
        self.browser.find_element(By.XPATH, "//span[text()='"+submenu_name+"']/..").click()

        return self.browser

    def addDepot(self):
        self.browser.find_element(By.XPATH, "//button[text()='添加']").click()

        self.browser.find_elements_by_name('depot_name')[0].send_keys('1234')
        self.browser.find_elements_by_name('depot_code')[0].send_keys('1234')

        self.browser.find_element(By.XPATH, "//button[@class='btn btn-info' and text()='保存']").click()

        return self.browser
