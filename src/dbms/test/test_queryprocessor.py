import unittest

from queryprocessor import *

class TestQueryProcessor(unittest.TestCase):
    def setUp(self):
        self.qp = QuerryProcessor('test/testData/test_db.data')
        self.qp.createTable('Person', ('id', DataType.INTEGER, True),
            ('name', DataType.STRING, True), ('age', DataType.INTEGER, True),
            ('hobbie', DataType.STRING, False))
        self.qp.addToTable('Person', ('id', 1), ('name', 'Alice'), ('age', 21),
            ('hobbie', 'embroider kokoshnik') )

    def tearDown(self):
        del self.qp

    def testCreateTableRaises(self):
        self.qp.createTable('table1')
        with self.assertRaises(QuerryProcessorException):
            self.qp.createTable('table1')

    def testCreateTable(self):
        self.qp.createTable('Person11', ('id', DataType.INTEGER, True),
            ('name', DataType.STRING, True), ('age', DataType.INTEGER, True),
            ('hobbie', DataType.STRING, False))

        self.assertEqual(self.qp.tables['Person'].name, 'Person')

    def testSaveLoadTables(self):
        self.qp.saveTables()
        self.qp.tables.clear()
        self.qp.loadTables()

    def testGetFromTable(self):
        self.assertEqual(len(self.qp.getFromTable('Person', ('name', 'Alice'))), 1)

        self.qp.addToTable('Person', ('id', 2), ('name', 'Alice'), ('age', 22),
            ('hobbie', 'quake II and kokoshniki') )

        self.assertEqual(len(self.qp.getFromTable('Person', ('name', 'Alice'))), 2)

    def testDeleteFromTable(self):
        self.assertEqual(len(self.qp.getFromTable('Person', ('name', 'Alice'))), 1)

        self.qp.addToTable('Person', ('id', 2), ('name', 'Alice'), ('age', 22),
            ('hobbie', 'quake II and kokoshniki') )
        self.assertEqual(len(self.qp.getFromTable('Person', ('name', 'Alice'))), 2)

        self.qp.deleteFromTable('Person', ('id', 2))
        self.assertEqual(len(self.qp.getFromTable('Person', ('name', 'Alice'))), 1)

    def testAddToTable(self):
        self.qp.addToTable('Person', ('id', 2), ('name', 'Bob'), ('age', 22),
            ('hobbie', 'quake II') )

    def testWrongTable(self):
        with self.assertRaises(QuerryProcessorException):
            self.qp.addToTable('WrongName', ('id', 1))

        with self.assertRaises(QuerryProcessorException):
            self.qp.getFromTable('WrongName', ('id', 1))
