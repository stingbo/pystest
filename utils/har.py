# coding = utf-8
import logging


class Log:
    def logHar(har):
        for entry in har['log']['entries']:
            _url = entry['request']['url']
            # 根据URL找到数据接口
            if "supplier" in _url:
                _response = entry['response']
                logging.info(_url)
                logging.info(_response['content'])