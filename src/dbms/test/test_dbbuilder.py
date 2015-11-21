import unittest

from queryprocessor import *
from dbbuilder import *

class TestDBBuilder(unittest.TestCase):
    def setUp(self):
        #open('test/testData/test_final_db.data', 'w').close()
        self.qp = QueryProcessor('test/testData/test_final_db.data')

    def tearDown(self):
        del self.qp

    @unittest.skip
    def testCreateTables(self):
        dbuilder = DBBuilder()
        dbuilder.buildTables(self.qp)
        dbuilder.makeSimpleData(self.qp)
        self.qp.saveTables()

        qr_article = self.qp.getFromTable('article', )
        qr_author = self.qp.getFromTable('author', )
        qr_article_author = self.qp.getFromTable('article_author', )

        qr_res = qr_article_author.join(qr_article, 'article_id', 'id')
        qr_res = qr_res.join(qr_author, 'author_id', 'id')

        qr_res = qr_res.project('article_id', 'paper_title', 'year', 'name')

        qr_res = qr_res.sort('article_id')

        for q in qr_res:
            print(q)

    @unittest.skip
    def testLoadTables(self):
        self.qp.loadTables()

        qr_article = self.qp.getFromTable('article', )
        qr_author = self.qp.getFromTable('author', )
        qr_article_author = self.qp.getFromTable('article_author', )

        qr_res = qr_article_author.join(qr_article, 'article_id', 'id')
        qr_res = qr_res.join(qr_author, 'author_id', 'id')

        qr_res = qr_res.project('article_id', 'paper_title', 'year', 'name')

        qr_res = qr_res.sort('article_id')

        for q in qr_res:
            print(q)
