# coding = utf-8
import json
import random
import string

class Util:
    def randstr(self, len = 5):
        len = int(len)
        return ''.join(random.sample(string.ascii_letters + string.digits, len))

    def phone(self):
        first = 1
        second = random.choice([3,4,5,6,7,8,9])
        third = {
            3:random.randint(0,9),
            4:random.choice([5,7]),
            5:random.choice([0,1,2,3,5,6,7,8,9]),
            6:random.randint(0,9),
            7:random.choice([6,7,8]),
            8:random.randint(0,9),
            9:random.randint(0,9),
        }[second]
        behind = ''
        for i in range(8):
            behind = behind + str(random.randint(0,9))

        phone = str(first) + str(second) + str(third) + behind

        return phone

    def randinterger(self, max = 9999):
        return random.randint(1, int(max))

    # 递归合并两个dict
    def recursionMergeTwoDict(x, y):
        # type: (dict, dict) -> dict
        z = dict()
        for key in x.keys():
            if key in y.keys():
                # 合并同类项
                x_value = x[key]
                y_value = y[key]
                if isinstance(x_value, dict) and isinstance(y_value, dict):
                    result_x_y = Util.recursionMergeTwoDict(x_value, y_value)
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
                if isinstance(x_value, dict) and isinstance(y_value, dict):
                    result_x_y = Util.recursionMergeTwoDict(x_value, y_value)
                else:
                    result_x_y = y_value
                z[key] = result_x_y
            else:
                z[key] = y[key]

        return z

    # 格式化dict格式
    def pretty(d):
        return json.dumps(d, indent=4, ensure_ascii=False)
