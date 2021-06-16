# coding = utf-8
import os
import yaml
from utils.util import Util


def getFileName(path):
    config_files = os.listdir(path)
    all_test_files = []
    for name in config_files:
        index = name.rfind('.')
        all_test_files.append(name[:index])
    return all_test_files


def getAllTestCase(path, files):
    test_cases = []
    for fl in files:
        config_file = "/config/" + fl + ".yaml"
        test_cases.append(path + config_file)
    return test_cases


class TestConfig:
    def __init__(self, path):
        self.path = path

    def get_test_case(self, argv):
        # 全局config文件
        global_config = {}
        global_config_file_path = self.path + "/config.yaml"
        if os.path.isfile(global_config_file_path):
            gf = open(global_config_file_path, 'r', encoding='utf-8')
            global_config = yaml.safe_load(gf.read())

        # 所有不含后缀名称的测试用例
        all_test_files = getFileName(self.path + '/config/')

        test_cases = []
        # 是否传入配置文件
        if len(argv) > 1:
            test_file = argv[1]
            # 执行所有测试用例
            if test_file == 'all_test':
                test_cases = getAllTestCase(self.path, all_test_files)
            else:  # 执行所传入的测试用例
                test_files = test_file.split(',')
                files = Util.list_diff(test_files, all_test_files)
                if len(files) > 0:
                    raise Exception(print('测试用例文件不存在: ', ', '.join(files)))

                test_cases = getAllTestCase(self.path, test_files)
        else:
            test_file = 'default'
            config_file = "/config/" + test_file + '.yaml'
            test_cases.append(self.path + config_file)

        # yaml配置文件是否存在
        configs = {}
        for test_case in test_cases:
            if not os.path.isfile(test_case):
                raise Exception(print('测试用例文件不存在: ' + test_case))

            f = open(test_case, 'r', encoding='utf-8')
            config = yaml.safe_load(f.read())

            # 合并配置
            configs = Util.recursionMergeTwoDict(configs, config)

        return Util.recursionMergeTwoDict(global_config, configs)
