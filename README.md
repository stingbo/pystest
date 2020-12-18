# 使用Python Selenium 进行自动化测试

## 快速开始

- 复制并修改配置，```cp config.example.yaml config.yaml```，此文件为全局配置，config目录下文件可覆盖此配置文件
- 使用：```python test.py config目录下的文件名```，默认使用default，python要求3.7版本以上

### 依赖

* 根据[HTMLTestRunner](https://pypi.org/project/HTMLTestRunner-Python3/)生成测试报告，报告目录为reports

* 安装[Selenium，文档](https://www.selenium.dev/documentation/zh-cn/)

* 安装WebDriver，[驱动下载地址](https://www.selenium.dev/documentation/zh-cn/webdriver/driver_requirements/)  
    另：Chromium/Chrome驱动需要翻墙，[附上镜像地址](http://npm.taobao.org/mirrors/chromedriver/)

* 安装[BrowserMob Proxy](https://github.com/lightbody/browsermob-proxy/releases/tag/browsermob-proxy-2.1.4)

#### 使用说明

* config目录下配置文件，格式说明：  

    > key: 字符串，菜单路径
    
    > name: 字符串，菜单名称，方便使用者查看配置使用
    
    > type: 字符串，寻找元素的方式，[与webdriver提供的一致](https://www.selenium.dev/documentation/zh-cn/getting_started_with_webdriver/locating_elements/)
    
    > content: 字符串，寻找元素所使用的内容，一次能够找到，有的路径通过一次找不到（指通用规则，不是绝对路径），则使用contents
    
    > contents: 数组，通过多次寻找元素所使用的内容
    
    > index: 整数，所找元素有可能是多个，使用index固定某一个，-1代表默认，-2代表所有，大于等于0，代表list下标
    
    > opertaion: 字符串，动作之前所要做的操作，数组类型，格式与上述一致
    
    > action: 字符串，要做的动作  
        1. open: 打开菜单，类似点击，但是可以增加一个open配置项，里面配置判断标识，目前实现了class判断，如果有此class，则不会点击，目的是防止某个菜单如果打开了，再点击则会关闭  
        2. click: 点击元素  
        3. moveToClick: 移动到目标元素并点击元素  
        4. sendKeys: 向能输入的地方填写某个值，详细说明见下方value  
    
    > value: 字符串，如果action是sendKeys，则需要value，value可以使用自定义函数，如pkgpath:utils.util.Util:randstr:6(from utils.util import Util && Util.randstr(6))

    > javascript: 字符串，javascript代码，如："arguments[0].scrollIntoView();"，目前支持简单javascript代码运行，复杂的需要自己修改，如果当前配置项获取是多个元素，则都会执行此javascript
    
    > listener: 数组，所需要监听的api url与返回的code，使用listener必须安装BrowserMob Proxy，并配置正确应用路径

    > iframe: 字符串，iframe的id或者name，配置后会运行切换到iframe操作

    > wait 对象，等待加载的元素，含有type与content（含义同上），比如等待某元素出现

    > wait_disappear 对象，等待消失的元素，含有type与content（含义同上），比如等待遮罩层的消失
    
#### 总结

* _使用contents多次获取元素时，在上一次范围内获取元素，使用 .//(点+双斜线)_
* _使用class匹配时，如果class里有空格，配置xpath时也需要含有，或者使用contains_ 
* 使用安全基本都能在config目录下里的文件找到，祝使用愉快，如果有问题，欢迎提issue
