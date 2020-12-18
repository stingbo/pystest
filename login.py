# coding = utf-8
from time import sleep
from selenium import webdriver

# 不使用框架使用python与selenium使用方式
browser = webdriver.Chrome()
browser.maximize_window()
browser.get("http://your.test.url")

sleep(0.3)
browser.find_elements_by_class_name('form-group')[4].find_element_by_tag_name(
    'input').send_keys('xxxx')
sleep(0.3)
browser.find_elements_by_class_name('form-group')[5].find_element_by_tag_name(
    'input').send_keys('xxxx')

sleep(0.3)
browser.find_elements_by_class_name('form-group')[7].find_element_by_tag_name(
    'button').click()

sleep(5)
browser.quit()
