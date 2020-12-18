# coding = utf-8
import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class Element:
    def __init__(self, browser):
        self.browser = browser

    # 获取元素
    def get(self, type, content, index, config={}, element={}):
        msg = 'type:' + type + ',index:' + str(index) + ',content:' + content
        if config and 'contents' in config.keys():
            contents = config.get('contents')
            for op in contents:
                element = self.get(op.get('type'), op.get('content'),
                                   op.get('index'), {}, element)
        else:
            if element:
                if index >= 0:
                    try:
                        result = element.find_elements(self.getType(type),
                                                       content)
                        return result[index]
                    except NoSuchElementException:
                        print(msg + ',元素不存在')
                    except IndexError:
                        print(msg + ',元素不存在或超出list限制')
                        os._exit(0)
                elif index == -2:
                    return element.find_elements(self.getType(type), content)
                else:
                    return element.find_element(self.getType(type), content)
            else:
                if index >= 0:
                    try:
                        result = self.browser.find_elements(
                            self.getType(type), content)
                        return result[index]
                    except NoSuchElementException:
                        print(msg + ',元素不存在')
                    except IndexError:
                        print(msg + ',元素不存在或超出list限制')
                        os._exit(0)
                elif index == -2:
                    return self.browser.find_elements(self.getType(type),
                                                      content)
                else:
                    return self.browser.find_element(self.getType(type),
                                                     content)

        return element

    def getType(self, type):
        if type == 'id':
            return By.ID
        elif type == 'class name':
            return By.CLASS_NAME
        elif type == 'xpath':
            return By.XPATH
        elif type == 'link text':
            return By.LINK_TEXT
        elif type == 'partial link text':
            return By.PARTIAL_LINK_TEXT
        elif type == 'name':
            return By.NAME
        elif type == 'tag name':
            return By.TAG_NAME
        elif type == 'css selector':
            return By.CSS_SELECTOR
        else:
            print('获取元素type错误：' + type)
