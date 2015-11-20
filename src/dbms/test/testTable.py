import unittest

from dataentry import *
from table import *

class TestTable(unittest.TestCase):
    def setUp(self):
        self.t = Table('table')
        self.assertEqual(self.t.name, 'table')

        self.t.addColumn('id', DataType.INTEGER, True)
        self.t.addColumn('name', DataType.STRING, True)
        self.t.addColumn('age', DataType.INTEGER, True)
        self.t.addColumn('hobbie', DataType.STRING, False)

    def tearDown(self):
        pass

    def testCreate(self):
        self.assertEqual(len(self.t.colTypes), 4)
        self.assertEqual(len(self.t.colIndexes), 3)

    def testWrongAdd(self):
        #correct
        self.t.add(DataEntry(1, 1), ('id', 1), ('name', 'Bob'), ('age', 22),
            ('hobbie', 'fishing'))

        #too few columns
        with self.assertRaises(TableException):
            self.t.add(DataEntry(1, 1), ('id', 1), ('name', 'Bob'), ('age', 22))

        #wrong column name
        with self.assertRaises(TableException):
            self.t.add(DataEntry(1, 1), ('id', 1), ('name', 'Bob'), ('age', 22),
            ('WRONG_COLNAME_hobbie', 'fishing'))

    def testAddGet(self):
        self.t.add(DataEntry(1, 11), ('id', 1), ('name', 'Alice'), ('age', 11),
            ('hobbie', 'singing'))
        self.t.add(DataEntry(2, 22), ('id', 22), ('name', 'Bob'), ('age', 22),
            ('hobbie', 'fishing'))
        self.t.add(DataEntry(3, 33), ('id', 333), ('name', 'Cidney'), ('age', 333),
            ('hobbie', 'nope'))

        self.assertTrue(DataEntry(1, 11) in self.t.get('id', 1))
        self.assertTrue(DataEntry(2, 22) in self.t.get('id', 22))
        self.assertTrue(DataEntry(3, 33) in self.t.get('id', 333))

        self.assertTrue(DataEntry(1, 11) in self.t.get('name', 'Alice'))
        self.assertTrue(DataEntry(2, 22) in self.t.get('name', 'Bob'))
        self.assertTrue(DataEntry(3, 33) in self.t.get('name', 'Cidney'))

        self.assertTrue(DataEntry(1, 11) in self.t.get('age', 11))
        self.assertTrue(DataEntry(2, 22) in self.t.get('age', 22))
        self.assertTrue(DataEntry(3, 33) in self.t.get('age', 333))

        #nonsearchable column
        with self.assertRaises(TableException):
            self.t.get('hobbie', 'fishing')

        #check types
        with self.assertRaises(TableException):
            self.t.get('id', '11')
        with self.assertRaises(TableException):
            self.t.get('name', 11)

    def testDeleteSimple(self):
        self.t.add(DataEntry(1, 11), ('id', 1), ('name', 'Alice'), ('age', 11),
            ('hobbie', 'singing'))
        self.t.add(DataEntry(2, 22), ('id', 22), ('name', 'Bob'), ('age', 22),
            ('hobbie', 'fishing'))
        self.t.add(DataEntry(3, 33), ('id', 333), ('name', 'Cidney'), ('age', 333),
            ('hobbie', 'nope'))

        self.t.delete('id', 22)

        self.assertTrue(DataEntry(1, 11) in self.t.get('id', 1))
        self.assertTrue(DataEntry(2, 22) not in self.t.get('id', 22))
        self.assertTrue(DataEntry(3, 33) in self.t.get('id', 333))

        self.assertTrue(DataEntry(1, 11) in self.t.get('name', 'Alice'))
        self.assertTrue(DataEntry(2, 22) not in self.t.get('name', 'Bob'))
        self.assertTrue(DataEntry(3, 33) in self.t.get('name', 'Cidney'))

        self.assertTrue(DataEntry(1, 11) in self.t.get('age', 11))
        self.assertTrue(DataEntry(2, 22) not in self.t.get('age', 22))
        self.assertTrue(DataEntry(3, 33) in self.t.get('age', 333))

    def testDeleteMultiple(self):
        self.t.add(DataEntry(1, 11), ('id', 1), ('name', 'Alice'), ('age', 11),
            ('hobbie', 'singing'))
        self.t.add(DataEntry(2, 22), ('id', 22), ('name', 'Bob'), ('age', 22),
            ('hobbie', 'fishing'))
        self.t.add(DataEntry(3, 33), ('id', 333), ('name', 'Cidney'), ('age', 333),
            ('hobbie', 'nope'))
        self.t.add(DataEntry(4, 44), ('id', 4444), ('name', 'Cidney'), ('age', 44),
            ('hobbie', 'nope'))
        self.t.add(DataEntry(5, 55), ('id', 5555), ('name', 'Cidney'), ('age', 55),
            ('hobbie', 'nope'))

        self.t.delete('name', 'Cidney')

        self.assertTrue(DataEntry(1, 11) in self.t.get('id', 1))
        self.assertTrue(DataEntry(2, 22) in self.t.get('id', 22))
        self.assertTrue(DataEntry(3, 33) not in self.t.get('id', 333))
        self.assertTrue(DataEntry(4, 44) not in self.t.get('id', 4444))
        self.assertTrue(DataEntry(5, 55) not in self.t.get('id', 5555))
