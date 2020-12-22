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
                    logging.info('请求地址：' + _url)
                    _request = entry['request']
                    logging.info('GET参数:%s' % _request.get('queryString', ''))
                    logging.info('POST参数:%s' % _request.get('postData', ''))
                    _response = entry['response']
                    logging.info('返回数据:%s' % _response['content'])
                    if 'text' in _response['content'].keys():
                        result = json.loads(_response['content']['text'])
                        self.assertEqual(code,
                                         result['code'],
                                         msg='接口请求失败:' +
                                         _response['content']['text'])
                    else:
                        print('没有获取到返回数据')
