# coding = utf-8
from time import sleep
from selenium import webdriver

browser = webdriver.Chrome()
browser.maximize_window()
browser.get("http://47.104.80.33:3002/#/")

sleep(0.3)
browser.find_elements_by_class_name('form-group')[4].find_element_by_tag_name('input').send_keys('17600113608')
sleep(0.3)
browser.find_elements_by_class_name('form-group')[5].find_element_by_tag_name('input').send_keys('123456')

sleep(0.3)
browser.find_elements_by_class_name('form-group')[7].find_element_by_tag_name('button').click()

sleep(5)
browser.quit()
