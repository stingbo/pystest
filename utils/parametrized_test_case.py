# coding = utf-8
import unittest


class ParametrizedTestCase(unittest.TestCase):  #可参数化的类
    """ TestCase classes that want to be parametrized should
    inherit from this class.
    """
    def __init__(self, methodName='runTest', param=None):
        super(ParametrizedTestCase, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_klass, defName=None, param=None):  #参数化方法
        """ Create a suite containing all tests taken from the given
        subclass, passing them the parameter 'param'
        """
        testLoader = unittest.TestLoader()
        testNames = testLoader.getTestCaseNames(testcase_klass)
        suite = unittest.TestSuite()
        if defName != None:
            for name in testNames:
                if name == defName:
                    suite.addTest(testcase_klass(name, param=param))
                else:
                    for name in testNames:
                        suite.addTest(testcase_klass(name, param=param))

        return suite
