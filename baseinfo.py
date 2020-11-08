# coding = utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait #等待页面加载某些元素

class BaseInfo:
    def companyInfo(browser, config):
        # 显式等待元素加载
        wait = WebDriverWait(browser, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'el-submenu')))

        icon = config.get('MENU').get('BASE_INFO').get('icon')
        browser.find_elements_by_class_name(icon)[0].click()

        name = config.get('MENU').get('BASE_INFO').get('submenu')[0].get('name')
        browser.find_element(By.XPATH, "//span[text()='"+name+"']/..").click()

        return browser
