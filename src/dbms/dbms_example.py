from queryprocessor import *
from dbbuilder import *

filename = 'test/testData/test_final_db.data' # default filename

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

def printQueryResult(qr):
    colStr = '|'
    for c in qr.columns:
        colStr += c + ' | '
    print(colStr)
    for r in qr:
        print(r)

if __name__ == '__main__':
    qp = QueryProcessor(filename)
    qp.loadTables()
    
    qr_res = qp.getFromTable('author', ('name', author.strip()))
    qr_res = qr_res.project('id')
    qr_res = qr_res.sort('id')
    printQueryResult(qr_res)
	
    """
    qr_article = qp.getFromTable('article', )
    qr_author = qp.getFromTable('author', )
    qr_article_author = qp.getFromTable('article_author', )

    qr_res = qr_article_author.join(qr_article, 'article_id', 'id')
    qr_res = qr_res.join(qr_author, 'author_id', 'id')

    qr_res = qr_res.project('article_id', 'paper_title', 'year', 'name')

    qr_res = qr_res.sort('name')
    qr_res = qr_res.sort('article_id')
	

    printQueryResult(qr_res)
	"""
    # printTables(qp, 'author')
