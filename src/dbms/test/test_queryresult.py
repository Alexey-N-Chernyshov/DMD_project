import unittest

from queryprocessor import *

class TestQueryResult(unittest.TestCase):
    def setUp(self):
        self.qp = QueryProcessor('test/testData/test_db.data')
        self.qp.createTable('Person', ('id', DataType.INTEGER, True),
            ('name', DataType.STRING, True), ('age', DataType.INTEGER, True),
            ('hobbie', DataType.STRING, False))
        self.qp.addToTable('Person', ('id', 1), ('name', 'Alice'), ('age', 21),
            ('hobbie', 'embroider kokoshnik'))
        self.qp.addToTable('Person', ('id', 2), ('name', 'Bob'), ('age', 22),
            ('hobbie', 'dota'))
        self.qp.addToTable('Person', ('id', 2), ('name', 'Charlie'), ('age', 33),
            ('hobbie', 'cartoons'))

        self.qp.createTable('BeerLike', ('beer', DataType.STRING, True),
            ('id_pers', DataType.INTEGER, True))
        self.qp.addToTable('BeerLike', ('beer', 'with vodka'), ('id_pers', 1))
        self.qp.addToTable('BeerLike', ('beer', 'any'),  ('id_pers', 2))

    @unittest.skip
    def testJoin(self):
        qres1 = self.qp.getFromTable('Person')
        qres2 = self.qp.getFromTable('BeerLike')

        with self.assertRaises(QueryResultException):
            qres1.join(qres2, 'WRONG_id', 'id_pers')

        with self.assertRaises(QueryResultException):
            qres1.join(qres2, 'id', 'WRONG_id_pers')

        #print(qres2.join(qres1, 'id_pers', 'id'))
        print(qres1.join(qres2, 'id', 'id_pers').columns)
        print(qres1.join(qres2, 'id', 'id_pers').data)

    @unittest.skip
    def testProject(self):
        qres1 = self.qp.getFromTable('Person')
        qres2 = self.qp.getFromTable('BeerLike')

        qres = qres1.join(qres2, 'id', 'id_pers')

        with self.assertRaises(QueryResultException):
            qres.project('id', 'WRONG_id')

        print(qres.project('beer', 'name', 'id').columns)
        print(qres.project('beer', 'name', 'id').data)

    @unittest.skip
    def testSort(self):
        qres1 = self.qp.getFromTable('Person')
        qres2 = self.qp.getFromTable('BeerLike')

        qres = qres1.join(qres2, 'id', 'id_pers')

        with self.assertRaises(QueryResultException):
            qres.sort('WRONG_id')

        print(qres.sort('id', reverse=True).columns)
        print(qres.sort('id', reverse=True).data)

        print(qres.sort('age').columns)
        print(qres.sort('age').data)

        print(qres.sort('beer').columns)
        print(qres.sort('beer').data)

    @unittest.skip
    def testGroupBy(self):
        self.qp.addToTable('Person', ('id', 2), ('name', 'Charlie'), ('age', 444),
            ('hobbie', 'none'))

        qres1 = self.qp.getFromTable('Person')
        qres2 = self.qp.getFromTable('BeerLike')

        qres = qres1.join(qres2, 'id', 'id_pers')

        with self.assertRaises(QueryResultException):
            qres.groupBy('WRONG_id')

        print(qres.groupBy('id', 'name').columns)
        print(qres.groupBy('id', 'name').data)

    @unittest.skip
    def testLimit(self):
        self.qp.addToTable('Person', ('id', 2), ('name', 'Charlie'), ('age', 444),
            ('hobbie', 'none'))

        qres1 = self.qp.getFromTable('Person')
        qres2 = self.qp.getFromTable('BeerLike')

        qres = qres1.join(qres2, 'id', 'id_pers')

        with self.assertRaises(QueryResultException):
            qres.groupBy('WRONG_id')

        print(qres.columns)
        print(qres.data)

        qres = qres.limit(1, 3)

        print(qres.columns)
        print(qres.data)

    @unittest.skip
    def testIter(self):
        self.qp.addToTable('Person', ('id', 2), ('name', 'Charlie'), ('age', 444),
            ('hobbie', 'none'))

        qres1 = self.qp.getFromTable('Person')
        qres2 = self.qp.getFromTable('BeerLike')

        qres = qres1.join(qres2, 'id', 'id_pers')

        for q in qres:
            print(q)
