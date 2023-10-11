import unittest

from k import sayhello


class SayHelloTestCase(unittest.TestCase):  # 测试用例
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sayhello(self):
        rv = sayhello()
        self.assertEqual(rv, "Hello!")

    def test_sqyhello_to_somebody(self):
        rv = sayhello(to='Grey')
        self.assertEqual(rv, "hello, Grey!")


if __name__ == '__main__':
    unittest.main()
