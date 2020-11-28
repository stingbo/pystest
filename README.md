# 使用Selenium进行自动化测试

1. 安装Selenium，[Selenium文档](https://www.selenium.dev/documentation/zh-cn/)

2. 安装WebDriver，[驱动下载地址](https://www.selenium.dev/documentation/zh-cn/webdriver/driver_requirements/)  
    另：Chromium/Chrome驱动需要外网，[附上镜像地址](http://npm.taobao.org/mirrors/chromedriver/)

3. 安装BrowserMob Proxy，[下载地址](https://github.com/lightbody/browsermob-proxy/releases/tag/browsermob-proxy-2.1.4)

#### 使用步骤

1. 复制并修改配置，```cp config.example.yaml config.yaml```，此文件为全局配置，config目录下文件可覆盖此配置文件

2. 使用：```python test.py config下的文件名```，默认使用default，python要求3.7版本以上

3. config目录下配置文件，格式说明：  
    key:菜单路径  
    name:菜单名称，方便使用者查看配置使用  
    type:寻找元素的方式，[与webdriver提供的一致](https://www.selenium.dev/documentation/zh-cn/getting_started_with_webdriver/locating_elements/)  
    content:寻找元素所使用的内容  
    contents:通过多次寻找元素所使用的内容  
    index:所找元素有可能是多个，使用index固定某一个，-1代表默认，-2代表所有，大于0，代表list下标  
    value:如果action是sendKeys，则需要value，value可以使用自定义函数，如pkgpath:utils.util.Util:randstr:6(from utils.util import Util && Util.randstr(6))  
    opertaion:动作之前所要做的操作，数组类型，格式与上述一致
    action:要做的动作(click,sendKeys,open,moveToClick,sendListKeys)  
    
#### 注意

1. _#.//表示在上一个获取的元素范围内再获取_
2. _#使用class匹配时，如果class里有空格，这里也需要有_ 
