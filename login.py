# coding = utf-8
import yaml
import os
from selenium import webdriver

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

browser.find_elements_by_class_name('form-group')[7].find_element_by_tag_name('button').click()
#browser.quit()
