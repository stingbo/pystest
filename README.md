# 使用Python Selenium 进行自动化测试

## 快速开始

- 复制并修改全局配置，```cp config.example.yaml config.yaml```，此文件为全局配置，config目录下文件可覆盖此配置

- 使用：```python test.py filename```，filename 为项目 config 目录下的文件名，如`python3 test.py default`，没有输入文件名，
则默认使用`default.yaml`，可以同时执行多个测试用例，如`python3 test.py test1,test2,test3`，或者执行 config 目录下所有的测试
用例：`python3 test.py all_test`

- 测试用例采用YAML通用格式编写，详见[YAML示例](#YAML示例)

### 依赖

* python要求3.7版本以上

* 根据[HTMLTestRunner](https://pypi.org/project/HTMLTestRunner-Python3/)生成测试报告，报告目录为 reports

* 安装[Selenium，文档](https://www.selenium.dev/documentation/zh-cn/)

* 安装WebDriver，[驱动下载地址](https://www.selenium.dev/documentation/zh-cn/webdriver/driver_requirements/)  
    另：Chromium/Chrome驱动需要翻墙，[附上镜像地址](http://npm.taobao.org/mirrors/chromedriver/)

* 安装[BrowserMob Proxy](https://github.com/lightbody/browsermob-proxy/releases/tag/browsermob-proxy-2.1.4)，代理监听使用，方便获取接口数据使用

#### 使用说明

* 框架运行逻辑：

    > 1. 获取配置，合并配置项，启动浏览器

    > 2. wait_disappear 是否配置等待消失

    > 3. iframe 是否配置切换iframe

    > 4. wait 是否配置等待加载

    > 5. listener 是否配置监听，配置则开启监听

    > 6. 根据 type，content，index 查找元素

    > 7. javascript 是否配置，是则执行 javascript

    > 8. 根据 action 执行动作

* 配置文件内容分为四类，格式说明如下：  
    1. BROWSER，对浏览器层的设置
    
        > type: 字符串，使用浏览器类型，目前支持 `Chrome/Firefox`
                                                          
        > bmp_path: 字符串，`browsermob_proxy` 地址，代理使用，获取 api 请求使用
                                                          
        > proxy: 布尔，`True/False`，是否开启代理
                                                          
        > h5: 布尔，`True/False`，是否使用 h5 进行测试打开浏览器
                                                          
        > device_name: 字符串，h5 模式下模拟的设备名称，目前只有在Chrome下生效，Firefox实现的策略是修改user_agent并设置浏览器界面大小
    
    2. WEBSITE，启动页面的设置
    
        > url: 字符串，启动页地址，目前只有这一个配置可用
    
    3. MENU，测试用例详情
    
        > key: 字符串，菜单路径
        
        > name: 字符串，菜单名称/功能名称，方便使用者查看配置使用
        
        > type: 字符串，寻找元素的方式，[与webdriver提供的一致](https://www.selenium.dev/documentation/zh-cn/getting_started_with_webdriver/locating_elements/)
        
        > content: 字符串，上述type对应寻找元素所使用的内容，且一次能够找到，有的路径通过一次找不到（指通用规则，不是绝对路径），则使用contents，配置为none则不会运行当前配置第 7 步查找元素后续流程，但会继续执行其它配置
        
        > contents: 数组，通过多次寻找元素所使用的内容
        
        > index: 整数，所找元素有可能是多个，使用index固定某一个，-1代表默认，-2代表所有，大于等于0，代表list下标
        
        > opertaion: 数组，action之前所要做的操作，数组类型，格式与上述一致
        
        > action: 字符串，要做的动作  
            1. none: 配置为none，不执行任务操作，如果配置了javascript选项，则会对元素执行javascript，因为action是最后才会执行  
            2. open: 打开菜单，类似点击，但是可以增加一个open配置项，里面配置判断标识，目前实现了class判断，如果有此class，则不会点击，目的是防止某个菜单如果打开了，再点击则会关闭  
            3. click: 点击元素  
            4. moveToClick: 移动到目标元素并点击元素  
            5. sendKeys: 向能输入的地方填写某个值，详细说明见下方value  
            5. modifyKeys: 同sendKeys，区别在于会先清空，详细说明见下方value  
            6. upload: 上传，value为上传的文件地址  
        
        > value: 字符串，如果action是sendKeys(输入)/modifyKeys(修改)，则需要value，value可以使用自定义方法，如pkgpath:utils.util.Util:randstr:6(from utils.util import Util && Util.randstr(6))，其它自定义方法见utils/util

        > javascript: 字符串，javascript代码，如："arguments[0].scrollIntoView();"，目前支持简单javascript代码运行，复杂的需要自己修改，如果当前配置项获取是多个元素，则都会执行此javascript
        
        > listener: 数组，所需要监听的api url与返回的code，使用listener必须安装BrowserMob Proxy，并配置正确应用路径

        > iframe: 字符串，iframe的id或者name，配置后会运行切换到对应iframe层操作，如果配置为空，则会保持在当前iframe层或者说时不做切换操作，如果没有配置，则会回到最外层

        > wait: 对象，等待加载的元素，含有type与content（含义同上），比如等待某元素出现

        > wait_disappear: 对象，等待消失的元素，含有type与content（含义同上），比如等待遮罩层的消失

        > wait_time: 数字，指定某个动作固定等待的时间，单位秒
    
    4. TEST，数组，具体执行的测试用例，如果`testa2`下还有`submenu`，则会自动获取并执行，多个文件的`TEST`配置
    会合并执行，执行顺序是输入测试用例时的名称顺序
        ```yaml
        TEST:
            - login
            - testa.testa1.testa2
            - testb.testb1.testb2
            - testc.testc1
        ```
    
#### YAML示例
```yaml
BROWSER:
    #浏览器类型
    type: Chrome/Firefox
    #bmp程序路径
    bmp_path: your/browsermob-proxy/path
    #是否开启代理，开启后，配置listener的操作，会记录请求日志到logs目录下
    proxy: True/False
    #H5
    H5: True/False
    #模拟的设备名称，目前只有在Chrome下生效，Firefox实现的策略是修改user_agent并设置浏览器界面大小
    device_name: iPhone 7

WEBSITE:
    #启动页地址
    url: http://www.your_website_url.com

MENU:
    login:
        key: login
        name: 登录
        type: xpath
        content: //button[@class='btn btn-primary' and text()='登录']
        index: -1
        action: click
        listener:
            -
                url: login/url
                code: 0
        operation:
            -
                name: 用户名
                type: tag name
                content: input
                value: xxxxx
                index: 2
                action: sendKeys
            -
                name: 密码
                type: tag name
                content: input
                value: xxxxx
                index: 3
                action: sendKeys
```
    
#### 总结

* _使用 contents 多次获取元素时，在上一次范围内获取元素，使用 .//(点+双斜线)_

* _使用 class 匹配时，如果 class 里有空格，配置 xpath 时也需要含有，或者使用 contains_ 

* _项目里 pre-commit.sample 文件为 git hook，`cp pre-commit.sample .git/hooks/pre-commit`，
依赖`yapf`与`pyflakes`，用于 python 代码语法与格式检测_

* _使用示例基本都能在 config 目录下里的文件找到，祝使用愉快，如果有问题或建议，欢迎提 issue_
