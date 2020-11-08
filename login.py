# coding = utf-8

class Login:
    def login(browser, config):
        url = config.get('WEBSITE').get('url')
        browser.get(url)

        username = config.get('WEBSITE').get('username')
        password = config.get('WEBSITE').get('password')
        browser.find_elements_by_class_name('form-group')[4].find_element_by_tag_name('input').send_keys(username)

        browser.find_elements_by_class_name('form-group')[5].find_element_by_tag_name('input').send_keys(password)

        # 登录
        browser.find_elements_by_class_name('form-group')[7].find_element_by_tag_name('button').click()

        return browser
