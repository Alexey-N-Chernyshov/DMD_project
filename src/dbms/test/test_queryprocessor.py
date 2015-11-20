import unittest

from queryprocessor import *

class TestQueryProcessor(unittest.TestCase):
    def setUp(self):
        self.qp = QuerryProcessor()

    def tearDown(self):
        pass

    def testCreateTableRaises(self):
        self.qp.createTable('table1')
        with self.assertRaises(QuerryProcessorException):
            self.qp.createTable('table1')

    def testCreateTableRaises(self):
        self.qp.createTable('Person', ('id', DataType.INTEGER, True),
            ('name', DataType.STRING, True), ('age', DataType.INTEGER, True),
            ('hobbie', DataType.STRING, False))
