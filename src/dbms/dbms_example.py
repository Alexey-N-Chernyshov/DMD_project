import time

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
    t = time.time()
    print(t)
	
	
id = 18
title = None
year = None
author = None
keyword = None
offset = 0
order = 'id'

qp = QueryProcessor(filename)
qp.loadTables()
qr_article_author = qp.getFromTable('article_author', )
# JOIN article_author, article ON article_id == article.id
query = []
if id:
    query.append(('id', id))
if title:
    query.append(('paper_title', title))
if year:
    query.append(('year', year))

qr_article = qp.getFromTable('article', *query)
qr_res = qr_article_author.join(qr_article, 'article_id', 'id')
# res (article_id, author_id, paper_title, year, venue)

# JOIN res, article_keyword ON article_id == article.id
qr_article_keyword = qp.getFromTable('article_keyword', )
qr_res = qr_res.join(qr_article_keyword, 'article_id', 'article_id')
# res (article_id, keyword_id, author_id, paper_title, year, venue)

# JOIN res, author ON author_id == author.id
query = []
if author:
    query.append(('name', author))
#if venue:
   # query.append(('venue', venue))
qr_author = qp.getFromTable('author', *query)
qr_res = qr_res.join(qr_author, 'article_id', 'id')
# res (article_id, keyword_id, author_id, name, institute, paper_title, year, venue)

# JOIN res, keyword ON keyword_id == keyword.id
query = []
if keyword:
    query.append(('tag', keyword))
qr_author = qp.getFromTable('keyword', *query)
qr_res = qr_res.join(qr_author, 'keyword_id', 'id')
# res (article_id, keyword_id, tag, author_id, name, institute, paper_title, year, venue)


qr_res = qr_res.project('article_id', 'paper_title', 'venue', 'year')
if order == 'id':
    qr_res.sort('article_id')
elif order == 'title':
    qr_res.sort('paper_title')
elif order == 'year':
    qr_res.sort('year')
qr_res = qr_res.groupBy('article_id', 'paper_title', 'venue', 'year')

qr_res.limit(offset, offset + 20)
  # cur.execute("""DELETE FROM reference
    #     WHERE from_id=%s AND to_id=%s""", (id, article_id))

    # qr_author = qp.getFromTable('author', )
    # qr_article_author = qp.getFromTable('article_author', )
    #
    # qr_res = qr_article_author.join(qr_article, 'article_id', 'id')
    # qr_res = qr_res.join(qr_author, 'author_id', 'id')
    #
    # qr_res = qr_res.project('article_id', 'paper_title', 'year', 'name')
    #
    # qr_res = qr_res.sort('article_id')
 
printQueryResult(qr_res)
	
    # printTables(qp, 'author')
