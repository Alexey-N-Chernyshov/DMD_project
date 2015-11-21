class SearchResultHandler(BaseHandler):
	def post(self):
		query = """SELECT article.id, paper_title, venue, year FROM
				article LEFT OUTER JOIN article_author ON article.id = article_author.article_id
				LEFT OUTER JOIN article_keyword ON article_keyword.article_id=article.id
				LEFT OUTER JOIN keyword ON keyword_id=keyword.id
				LEFT OUTER JOIN author ON author_id=author.id
				WHERE TRUE"""
			if id:
				query += ' AND article.id=' + id
			if title:
				query += """ AND paper_title='""" + title + """'"""
			if author:
				query += """ AND author.name='""" + author + """'"""
			if venue:
				query += """ AND venue='""" + venue + """'"""
			if year:
				query += ' AND year=' + year
			if keyword:
			   query += """ AND tag='""" + keyword + """'"""
			if order == 'id':
				query += ' ORDER BY article.id '
			elif order == 'title':
				query += ' ORDER BY article.paper_title '
			elif order == 'year':
				query += ' ORDER BY article.year '
			query += 'OFFSET ' + str(offset) + ' LIMIT 20'

"""============================================================
==============================================================="""

class AuthorHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
		cur.execute("""SELECT id, name, institute FROM author WHERE id=%s;""", (id, )) 
		qr_author = qp.getFromTable('author', )
		qr_res = qp.getFromTable('author', ('id', id))
		qr_res = qr_res.project('id', 'name', 'institute')
		qr_res = qr_res.sort('id')
		
		cur.execute("""SELECT article_id, article.paper_title
            FROM article_author JOIN article ON article_id=article.id
            WHERE author_id=%s""", (id, ))
		qr_article_author = qp.getFromTable('article_author', ('author_id', author_id))
		qr_article = qp.getFromTable('article')
		qr_res = qr_article_author.join(qr_article, 'article_id', 'id')
		qr_res = qr_res.project('article_id', 'paper_title')
		qr_res = qr_res.sort('article_id')
"""============================================================
==============================================================="""
	
class AuthorDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
	
	cur.execute("""DELETE FROM article_author WHERE author_id=%s""", (id, ))
	qp.deleteFromTable('article_author', ('author_id', author_id))
	
	cur.execute("""DELETE FROM author WHERE id=%s""", (id, ))
	qp.deleteFromTable('author', ('id', id))
"""============================================================
==============================================================="""

class AuthorUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
		cur.execute("""SELECT id, name, institute FROM author WHERE id=%s;""", (id, ))
		qr_res = qp.getFromTable('author', ('id', id))
		qr_res = qr_res.project('id', 'name', 'institute')
		qr_res = qr_res.sort('id')
		
		cur.execute("""SELECT article_id, article.paper_title
            FROM article_author JOIN article ON article_id=article.id
            WHERE author_id=%s""",
            (id,))
		qr_article_author = qp.getFromTable('article_author', ('author_id', author_id))
		qr_article = qp.getFromTable('article')
		qr_res = qr_article_author.join(qr_article, 'article_id', 'id')
		qr_res = qr_res.project('article_id', 'paper_title')
		qr_res = qr_res.sort('article_id')	
			
"""============================================================
==============================================================="""
	
class AuthorUpdateSaveHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""UPDATE author SET id=%s, name=%s, institute=%s
            WHERE id=%s""", (id, name, institute, id))
		qp.deleteFromTable('author', ('id', id))
		qp.addToTable('author', ('id', id), ('name', name), ('institute', institute))
		
"""============================================================
==============================================================="""

class AuthorUpdateAddArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""INSERT INTO article_author (author_id, article_id)
            VALUES (%s, %s)""", (id, article_id))
		qp.addToTable('article_author', ('id', id), ('article_id', article_id))
		
"""============================================================
==============================================================="""
class AuthorUpdateDeleteArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""DELETE FROM article_author
            WHERE author_id=%s AND article_id=%s""", (id, article_id))
			qp.`deleteFromTable('author', ('id', id), ('article_id', article_id))
			
			
"""============================================================
==============================================================="""

class ArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
		cur.execute("""SELECT * FROM article WHERE id=%s;""", (id, ))
		qr_article = qp.getFromTable('article',('id', id))

        cur.execute("""SELECT author.id,name FROM author, article_author
                           WHERE author_id=author.id AND  article_id=%s""", (id, ))
        qr_article_author = qp.getFromTable('article_author', ('article_id', article_id))
		qr_author = qp.getFromTable('author')
		qr_res = qr_author.join(qr_article_author, 'id', 'article_id')
		qr_res = qr_res.project('id', 'name')
		qr_res = qr_res.sort('id')	
		
        cur.execute("""SELECT to_id, paper_title FROM reference, article WHERE article.id=to_id AND from_id=%s""", (id, ))
		qr_reference = qp.getFromTable('reference', ('from_id', id))
		qr_article = qp.getFromTable('article')
		qr_res = qr_reference.join(qr_article, 'to_id', 'id')
		qr_res = qr_res.project('to_id', 'paper_title')
		qr_res = qr_res.sort('to_id')
		
        cur.execute("""SELECT from_id, paper_title FROM reference, article WHERE article.id=from_id AND to_id=%s""", (id, ))
		qr_reference = qp.getFromTable('reference', ('from_id', id))
		qr_article = qp.getFromTable('article')
		qr_res = qr_reference.join(qr_article, 'to_id', 'id')
		qr_res = qr_res.project('from_id', 'paper_title')
		qr_res = qr_res.sort('from_id')
		
        cur.execute("""SELECT tag FROM keyword, article_keyword
                            WHERE article_id=%s AND keyword_id=keyword.id""", (id, ))
		qr_article_keyword = qp.getFromTable('article_keyword', ('article_id', id))
		qr_keyword = qp.getFromTable('keyword')
		qr_res = qr_keyword.join(qr_article_keyword, 'id', 'keyword_id')
		qr_res = qr_res.project('tag')
		qr_res = qr_res.sort('tag')		
		
"""============================================================
==============================================================="""

class AddArticleHandler(BaseHandler):
	def post(self):

        cur.execute("""SELECT id FROM article ORDER BY id DESC LIMIT 1""")
		qr_res = qp.getFromTable('article')
		qr_res = qr_res.project('id')
		qr_res = qr_res.sort('id', reverse=True)		
		qr_res = qr_res.limit(0, 1)	
		
        cur.execute("""INSERT INTO article(id, paper_title, year, venue)
            VALUES (%s, %s, %s, %s);""", (id, title, year, venue))
		qp.addToTable('article', ('id', id), ('paper_title', title),('year', year) ,('venue', venue))

            cur.execute("""SELECT id from author WHERE name=%s""", (author.strip(),))
			qr_res = qp.getFromTable('author', ('name', author.strip()))
			qr_res = qr_res.project('id')
			qr_res = qr_res.sort('id')
			
                cur.execute("""INSERT INTO author(name, institute)
                    VALUES (%s, %s)""", (author, "NULL"))

                cur.execute("""SELECT id from author WHERE name=%s""", (author,))

            cur.execute("""INSERT INTO article_author(article_id, author_id)
                VALUES (%s, %s)""", (id, auth_id))
           
            cur.execute("""SELECT id from keyword WHERE tag=%s""", (keyword,))
            
                cur.execute("""INSERT INTO keyword(tag)
                    VALUES (%s)""", (keyword, ))
                
                cur.execute("""SELECT id from keyword WHERE tag=%s""", (keyword,))
                
            cur.execute("""INSERT INTO article_keyword(article_id, keyword_id)
                VALUES (%s, %s)""", (id, keyword_id))
                   
                cur.execute("""INSERT INTO reference(from_id, to_id)
                    VALUES (%s, %s)""", (id, int(ref_to)))
        
                cur.execute("""INSERT INTO reference(from_id, to_id)
                    VALUES (%s, %s)""", (id, int(ref_to)))
					
"""============================================================
==============================================================="""	

class ArticleDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""DELETE FROM article_author WHERE article_id=%s""", (id, ))

        cur.execute("""DELETE FROM article_keyword WHERE article_id=%s""", (id, ))

        cur.execute("""DELETE FROM reference WHERE from_id=%s OR to_id=%s""", (id, id))

        cur.execute("""DELETE FROM article WHERE id=%s""", (id, ))
"""============================================================
==============================================================="""

class ArticleUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
		cur.execute("""SELECT * FROM article WHERE id=%s;""", (id, ))
		
		cur.execute("""SELECT author.id,name FROM author, article_author
                           WHERE author_id=author.id AND  article_id=%s""", (id, ))
						   
		cur.execute("""SELECT to_id, paper_title FROM reference, article WHERE article.id=to_id AND from_id=%s""", (id, ))
		
		cur.execute("""SELECT from_id, paper_title FROM reference, article WHERE article.id=from_id AND to_id=%s""", (id, ))
		
		cur.execute("""SELECT tag FROM keyword, article_keyword
                            WHERE article_id=%s AND keyword_id=keyword.id""", (id, ))
"""============================================================
==============================================================="""

class ArticleUpdateSaveHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""UPDATE article SET id=%s, paper_title=%s, year=%s, venue=%s
            WHERE id=%s""", (id, title, year, venue, id))
"""============================================================
==============================================================="""

class ArticleUpdateAddAuthorHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""SELECT id FROM author WHERE name=%s""", (name, ))
		
		cur.execute("""INSERT INTO author(name, institute) VALUES
                (%s, %s)""", (name, "NULL"))
				
		cur.execute("""SELECT author_id  author WHERE author.name=%s""", (name, ))
		
		cur.execute("""INSERT INTO article_author (author_id, article_id)
                VALUES (%s, %s)""", (author_id[0], id))
"""============================================================
==============================================================="""

class ArticleUpdateDeleteAuthorHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""DELETE FROM article_author
            WHERE author_id=%s AND article_id=%s""", (author_id, id))
			
"""============================================================
==============================================================="""

class ArticleUpdateAddKeywordHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
	cur.execute("""SELECT id FROM keyword WHERE tag=%s""", (tag, ))
	
	cur.execute("""INSERT INTO keyword(tag) VALUES
                    (%s)""", (tag, ))
	
	cur.execute("""SELECT id FROM keyword WHERE tag=%s""", (tag, ))
	
	cur.execute("""INSERT INTO article_keyword (article_id, keyword_id)
                    VALUES (%s, %s)""", (id, tag_id[0]))
"""============================================================
==============================================================="""

class ArticleUpdateDeleteKeywordHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""SELECT id FROM keyword WHERE tag=%s""", (tag, ))
		
		cur.execute("""DELETE FROM article_keyword
            WHERE keyword_id=%s AND article_id=%s""", (keyword_id, id))
		
"""============================================================
==============================================================="""

class ArticleUpdateAddReftoHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        cur.execute("""INSERT INTO reference (from_id, to_id)
            VALUES (%s, %s)""", (id, article_id))
			
"""============================================================
==============================================================="""


class ArticleUpdateDeleteReftoHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""DELETE FROM reference
            WHERE from_id=%s AND to_id=%s""", (id, article_id))
			
"""============================================================
==============================================================="""

class ArticleUpdateAddReffromHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""INSERT INTO reference (from_id, to_id)
            VALUES (%s, %s)""", (article_id, id))
			
"""============================================================
==============================================================="""

class ArticleUpdateDeleteReffromHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""DELETE FROM reference
            WHERE from_id=%s AND to_id=%s""", (id, article_id))