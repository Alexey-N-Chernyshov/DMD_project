import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

from queryprocessor import *
from dbbuilder import *

filename = 'test/testData/test_final_final_db.data' # default filename
dbname = 'dmd_project'

def printTable(qp, tablename):
    qr = qp.getFromTable(tablename, )
    print(
        "============================================================================\n" +
        "Table " + tablename +
        "\n============================================================================")
    for q in qr:
        print(q)

def printTables(qp, *tablename):
    for t in tablename:
        printTable(qp, t)

if __name__ == '__main__':
    open(filename, 'w').close()

    qp = QueryProcessor(filename)
    dbuilder = DBBuilder()
    dbuilder.buildTables(qp)

    #Define our connection string
    conn_string = "host='localhost' dbname='" + dbname + "' user='postgres' password='postgres'"
    # print the connection string we will use to connect
    print("Connecting to database\n	->%s" % (conn_string))
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)
    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cur = conn.cursor()

    print("Loading article")
    cur.execute("""SELECT id, paper_title, year, venue FROM article;""")
    articles = cur.fetchall()
    for a in articles:
        qp.addToTable('article',
            ('id', a[0]),
            ('paper_title', a[1]),
            ('year', a[2]),
            ('venue', a[3]))

    print("Loading author")
    cur.execute("""SELECT id, name, institute FROM author;""")
    authors = cur.fetchall()
    for a in authors:
        qp.addToTable('author',
            ('id', a[0]),
            ('name', a[1]),
            ('institute', a[2]))

    print("Loading article_author")
    cur.execute("""SELECT article_id, author_id FROM article_author;""")
    authors = cur.fetchall()
    for a in authors:
        qp.addToTable('article_author',
            ('article_id', a[0]),
            ('author_id', a[1]))

    print("Loading article_keyword")
    cur.execute("""SELECT article_id, keyword_id FROM article_keyword;""")
    authors = cur.fetchall()
    for a in authors:
        qp.addToTable('article_keyword',
            ('article_id', a[0]),
            ('keyword_id', a[1]))

    print("Loading reference")
    cur.execute("""SELECT from_id, to_id FROM reference;""")
    authors = cur.fetchall()
    for a in authors:
        qp.addToTable('reference',
            ('from_id', a[0]),
            ('to_id', a[1]))

    print("Loading keyword")
    cur.execute("""SELECT id, tag FROM keyword;""")
    authors = cur.fetchall()
    for a in authors:
        qp.addToTable('keyword',
            ('id', a[0]),
            ('tag', a[1]))

    qp.saveTables()

    print("Loaded!")

    # printTables(qp, 'article', 'author', 'article_author', 'article_keyword',
    #     'reference', 'keyword')
