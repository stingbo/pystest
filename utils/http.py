# coding = utf-8
import logging
import json
import unittest


class Http(unittest.TestCase):
    def logHar(har):
        for entry in har['log']['entries']:
            _url = entry['request']['url']
            # 根据URL找到数据接口
            if "supplier" in _url:
                _response = entry['response']
                logging.info(_url)
                logging.info(_response['content'])

    def listener(self, har, listener):
        for ln in listener:
            apiurl = ln.get('url')
            code = ln.get('code')
            for entry in har['log']['entries']:
                _url = entry['request']['url']
                # 根据URL找到数据接口
                if apiurl in _url:
                    logging.info(_url)
                    _response = entry['response']
                    logging.info(_response['content'])
                    result = json.loads(_response['content']['text'])
                    self.assertEqual(code,
                                     result['code'],
                                     msg='接口请求失败:' +
                                     _response['content']['text'])
