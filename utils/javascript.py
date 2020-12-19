# coding = utf-8


class Javascript:
    def __init__(self, browser, element):
        self.browser = browser
        self.element = element

    # 给元素执行javascript代码
    def exjavascript(self, javascript):
        if isinstance(self.element, list):
            for el in self.element:
                self.exjs(el, javascript)
        else:
            self.exjs(self.element, javascript)

    # 给元素执行javascript代码
    def exjs(self, element, javascript):
        params = javascript.split('.')
        if params[0] == 'setAttribute':
            self.browser.execute_script(
                "arguments[0].setAttribute(arguments[1], arguments[2])",
                element, params[1], params[2])
        else:
            self.browser.execute_script(javascript, element)
