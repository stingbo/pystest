# coding = utf-8
import json
import random
import string


class Util:
    #随机字母字符串
    def randstr(self, params):
        len = int(params[0])
        return ''.join(random.sample(string.ascii_letters + string.digits,
                                     len))

    # 随机email
    def email(self):
        params = [8]
        str = self.randstr(params)
        return str + '@test.com'

    # 随机手机号
    def phone(self):
        first = 1
        second = random.choice([3, 4, 5, 6, 7, 8, 9])
        third = {
            3: random.randint(0, 9),
            4: random.choice([5, 7]),
            5: random.choice([0, 1, 2, 3, 5, 6, 7, 8, 9]),
            6: random.randint(0, 9),
            7: random.choice([6, 7, 8]),
            8: random.randint(0, 9),
            9: random.randint(0, 9),
        }[second]
        behind = ''
        for i in range(8):
            behind = behind + str(random.randint(0, 9))

        phone = str(first) + str(second) + str(third) + behind

        return phone

    # 生成随机整数
    def randinterger(self, params):
        max = int(params[0])
        return random.randint(1, max)

    # 生成随机中文字符串
    def randGBK2312(self, params):
        len = int(params[0])
        i = 1
        if len < i:
            len = i
        str = ''
        while i <= len:
            head = random.randint(0xb0, 0xf7)
            body = random.randint(0xa1, 0xfe)
            val = f'{head:x} {body:x}'
            str = str + bytes.fromhex(val).decode('gb2312')
            i += 1

        return str

    # 递归合并两个dict
    def recursionMergeTwoDict(x, y):
        z = dict()
        for key in x.keys():
            if key in y.keys():
                # 合并同类项
                x_value = x[key]
                y_value = y[key]
                if key == 'TEST':
                    if not x_value:
                        x_value = []
                    if not y_value:
                        y_value = []
                    x_value.extend(y_value)
                    if key in z.keys():
                        z['TEST'].extend(x_value)
                        z['TEST'] = list(set(z['TEST']))
                        z['TEST'].sort(key=z['TEST'].index)
                    else:
                        z['TEST'] = list(set(x_value))
                        z['TEST'].sort(key=x_value.index)
                else:
                    if isinstance(x_value, dict) and isinstance(y_value, dict):
                        result_x_y = Util.recursionMergeTwoDict(
                            x_value, y_value)
                    else:
                        result_x_y = y_value
                    z[key] = result_x_y
            else:
                z[key] = x[key]

        for key in y.keys():
            if key in x.keys():
                # 合并同类项
                x_value = x[key]
                y_value = y[key]
                if key == 'TEST':
                    pass
                else:
                    if isinstance(x_value, dict) and isinstance(y_value, dict):
                        result_x_y = Util.recursionMergeTwoDict(
                            x_value, y_value)
                    else:
                        result_x_y = y_value
                    z[key] = result_x_y
            else:
                z[key] = y[key]

        return z

    # 格式化dict格式
    def pretty(d):
        return json.dumps(d, indent=4, ensure_ascii=False)

    # 在list a中但不在b中
    def list_diff(a, b):
        return list(set(a).difference(set(b)))
