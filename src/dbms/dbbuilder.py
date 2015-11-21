from table import DataType

class DBBuilder:
    def buildTables(self, qp):
        qp.createTable('article',
            ('id', DataType.INTEGER, True),
            ('paper_title', DataType.STRING, True),
            ('year', DataType.INTEGER, True),
            ('venue', DataType.STRING, False))

        qp.createTable('article_author',
            ('article_id', DataType.INTEGER, True),
            ('author_id', DataType.INTEGER, True))

        qp.createTable('article_keyword',
            ('article_id', DataType.INTEGER, True),
            ('keyword_id', DataType.INTEGER, True))

        qp.createTable('author',
            ('id', DataType.INTEGER, True),
            ('name', DataType.STRING, True),
            ('institute', DataType.STRING, False))

        qp.createTable('keyword',
            ('id', DataType.INTEGER, True),
            ('tag', DataType.STRING, True))

        qp.createTable('reference',
            ('from_id', DataType.INTEGER, True),
            ('to_id', DataType.INTEGER, True))

    def makeSimpleData(self, qp):
        qp.addToTable('article',
            ('id', 0),
            ('paper_title', 'OQL[C++]: Extending C++ with an Object Query Capability.'),
            ('year', 1995),
            ('venue', 'Modern Database Systems'))

        qp.addToTable('article',
            ('id', 1),
            ('paper_title', 'Overview of the Iris DBMS.'),
            ('year', 1989),
            ('venue', 'Object-Oriented Concepts, Databases, and Applications'))

        qp.addToTable('article',
            ('id', 2),
            ('paper_title', 'Foundations of Databases.'),
            ('year', 1995),
            ('venue', ''))

        qp.addToTable('article',
            ('id', 3),
            ('paper_title', 'The Java Programming Language.'),
            ('year', 1996),
            ('venue', ''))

        qp.addToTable('article',
            ('id', 4),
            ('paper_title', 'Algorithms, 2nd Edition.'),
            ('year', 1988),
            ('venue', ''))

        #authors
        qp.addToTable('author',
            ('id', 0),
            ('name', 'Daniel H. Fishman'),
            ('institute', ''))

        qp.addToTable('author',
            ('id', 1),
            ('name', 'David Beech'),
            ('institute', ''))

        qp.addToTable('author',
            ('id', 2),
            ('name', 'Waqar Hasan'),
            ('institute', ''))

        qp.addToTable('author',
            ('id', 3),
            ('name', 'William Kent'),
            ('institute', ''))

        qp.addToTable('author',
            ('id', 4),
            ('name', 'Brom Mahbod'),
            ('institute', ''))

        #article - authors
        qp.addToTable('article_author',
            ('article_id', 0),
            ('author_id', 0))

        qp.addToTable('article_author',
            ('article_id', 1),
            ('author_id', 0))

        qp.addToTable('article_author',
            ('article_id', 1),
            ('author_id', 1))

        qp.addToTable('article_author',
            ('article_id', 2),
            ('author_id', 2))

        qp.addToTable('article_author',
            ('article_id', 3),
            ('author_id', 3))

        qp.addToTable('article_author',
            ('article_id', 3),
            ('author_id', 4))
