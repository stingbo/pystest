# coding = utf-8
import yaml
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys #键盘按键操作
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait #等待页面加载某些元素

class Login:

    def login():


# 当前脚本所在目录路径
curpath = os.path.dirname(os.path.realpath(__file__))
# yaml配置文件路径
yamlconfig = os.path.join(curpath, "config.yaml")

f = open(yamlconfig, 'r', encoding='utf-8')
config = yaml.safe_load(f.read())

browser = webdriver.Chrome()

url = config.get('WEBSITE').get('url')
browser.get(url)

username = config.get('WEBSITE').get('username')
password = config.get('WEBSITE').get('password')
browser.find_elements_by_class_name('form-group')[4].find_element_by_tag_name('input').send_keys(username)
browser.find_elements_by_class_name('form-group')[5].find_element_by_tag_name('input').send_keys(password)

# 登录
browser.find_elements_by_class_name('form-group')[7].find_element_by_tag_name('button').click()

# 显式等待元素加载
wait = WebDriverWait(browser, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'el-submenu')))

browser.find_elements_by_class_name('menu-icon-4')[0].click()

browser.find_element(By.XPATH, "//span[text()='企业信息']/..").click()

#browser.quit()
