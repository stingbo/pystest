# coding = utf-8
from utils.element import Element


class WaitDisappear:
    driver = None
    config = None

    def __init__(self, config) -> None:
        self.config = config
        super().__init__()

    def __call__(self, driver):
        self.driver = driver
        return self.waitElementDisappear()

    # 自定义，等待消失的元素
    def waitElementDisappear(self):
        el = Element(self.driver)
        element = el.get(self.config.get('type'), self.config.get('content'),
                         -1)
        style = element.get_attribute('style')
        # if element.is_displayed():
        #     print('元素未消失')
        #     return False
        # else:
        #     print('元素消失')
        #     return True
        if 'none' in style:
            return True
        else:
            return False
