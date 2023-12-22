# Automated Testing with Python Selenium
- Supports running on both PC and H5, fetching API data through proxies, headless mode, generating reports (including screenshots), sending emails, etc.
- Pull requests are welcome.
- [中文文档](README_CN.md)

## Quick Start

- Copy and modify the global configuration: `cp config.example.yaml config.yaml`. This file serves as the global configuration, and files in the `config` directory can override it.

- Use: `python test.py filename`, where `filename` is the name of the file in the project's `config` directory, e.g., `python3 test.py default`. If no filename is provided, it defaults to `default.yaml`.

- Test cases are written in YAML format. See [YAML Examples](#YAML-Examples) for details.

- Run existing test cases: `python3 test.py default,test1`, which opens Baidu, searches for "stingbo pystest", navigates to the GitHub directory, and finally opens the specified project.

## Other Commands

- View all test cases in the `config` directory: `python3 test.py ls`.

- Run multiple test cases simultaneously: `python3 test.py test1,test2,test3`.

- Execute test cases from a configuration file: `python3 test.py -f /your/path/test.txt`. The file content should be like:
    ```test.txt
    test1,test2,test3
    ```

- Run all test cases in the `config` directory: `python3 test.py all_test`.

### Dependencies

* Python 3.7 or above.

* [HTMLTestRunner](https://pypi.org/project/HTMLTestRunner-Python3/) for generating test reports. Reports are stored in the `reports` directory.

* [Selenium](https://www.selenium.dev/documentation/) for browser automation.

* WebDriver. Download from [here](https://chromedriver.chromium.org/downloads).

* [BrowserMob Proxy](https://github.com/lightbody/browsermob-proxy/releases/tag/browsermob-proxy-2.1.4) for proxying API requests.

#### Usage Instructions

* Framework logic:
    1. Retrieve and merge configurations, launch the browser.
    2. Check for `wait_disappear` configuration.
    3. Check for `iframe` configuration.
    4. Check for `wait` configuration.
    5. Check for `listener` configuration.
    6. Locate elements based on `type`, `content`, and `index`.
    7. Execute JavaScript if configured.
    8. Perform actions based on the `action` configuration.

* Configuration sections:
    1. **DEBUG**: Boolean, `True/False`. Enable debug mode.
    2. **IMAGE**: Boolean, `True/False`. Enable screenshots.
    3. **MAIL**: Email configuration for sending test reports.
    4. **BROWSER**: Browser-related settings.
    5. **WEBSITE**: Settings for the starting page.
    6. **MENU**: Test case details.
    7. **TEST**: Specific test cases to execute.

#### YAML Examples

```yaml
DEBUG: False
IMAGE: True

MAIL:
  SEND: True
  SMTP:
    username: send_notice@test.com
    password: xxxxxxxxxx
    host: smtp.163.com
    port: 25
  receiver:
    - receiver1@test.com
    - receiver2@test.com

BROWSER:
  type: Chrome
  bmp_path: your/browsermob-proxy/path
  proxy: True
  H5: True
  device_name: iPhone 7
  headless: True

WEBSITE:
  url: http://www.your_website_url.com

MENU:
  login:
    key: login
    name: Login
    type: xpath
    content: //button[@class='btn btn-primary' and text()='Login']
    index: -1
    action: click
    listener:
      - url: login/url
        code: 0
    operation:
      - name: Username
        type: tag name
        content: input
        value: xxxxx
        index: 2
        action: sendKeys
      - name: Password
        type: tag name
        content: input
        value: xxxxx
        index: 3
        action: sendKeys
```

#### Conclusion
* _Use contents to obtain elements within the scope of the previous one, using `.(dot + double slash)._

* _When matching with class, if the class contains spaces, include them in the xpath configuration, or use contains._

* _The pre-commit.sample file is a git hook. Copy it with cp pre-commit.sample .git/hooks/pre-commit. It relies on yapf and pyflakes for Python code syntax and format checking._

* _Examples of usage can be found in the files in the config directory. Feel free to use, and if you have any questions or suggestions, please open an issue._
