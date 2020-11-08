# coding = utf-8

import yaml
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys #键盘按键操作
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait #等待页面加载某些元素

from login import Login

# 当前脚本所在目录路径
curpath = os.path.dirname(os.path.realpath(__file__))
# yaml配置文件路径
yamlconfig = os.path.join(curpath, "config.yaml")

f = open(yamlconfig, 'r', encoding='utf-8')
config = yaml.safe_load(f.read())

browser = webdriver.Chrome()

Login.login(browser, config)

# 显式等待元素加载
wait = WebDriverWait(browser, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'el-submenu')))

browser.find_elements_by_class_name('menu-icon-4')[0].click()

browser.find_element(By.XPATH, "//span[text()='企业信息']/..").click()
