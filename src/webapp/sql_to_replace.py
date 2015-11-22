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



			qr_article_author = qp.getFromTable('article_author', )
			# JOIN article_author, article ON article_id == article.id
			query = []
			if id:
				query.apend(('id', id))
			if title:
				query.apend(('paper_title', title))
			if year:
				query.apend(('year', year))

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
				query.apend(('name', author))
			if venue:
				query.apend(('venue', venue))
			qr_author = qp.getFromTable('author', *query)
			qr_res = qr_res.join(qr_author, 'article_id', 'id')
			# res (article_id, keyword_id, author_id, name, institute, paper_title, year, venue)

			# JOIN res, keyword ON keyword_id == keyword.id
			query = []
			if keyword:
				query.apend(('tag', keyword))
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

			qr_res.limit(offset, offset + 20)

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
			qp.deleteFromTable('author', ('id', id), ('article_id', article_id))


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
				qp.addToTable('author', ('name', name), ('institute', "NULL"))

                cur.execute("""SELECT id from author WHERE name=%s""", (author,))
				qr_res = qp.getFromTable('author', ('name', author))
				qr_res = qr_res.project('id')
				qr_res = qr_res.sort('id')

            cur.execute("""INSERT INTO article_author(article_id, author_id)
                VALUES (%s, %s)""", (id, auth_id))
			qp.addToTable('article_author', ('article_id', id), ('author_id', auth_id))

            cur.execute("""SELECT id from keyword WHERE tag=%s""", (keyword,))
            qr_res = qp.getFromTable('keyword', ('tag', keyword))
			qr_res = qr_res.project('id')
			qr_res = qr_res.sort('id')

                cur.execute("""INSERT INTO keyword(tag)
                    VALUES (%s)""", (keyword, ))
				qp.addToTable('keyword', ('tag', keyword))

                cur.execute("""SELECT id from keyword WHERE tag=%s""", (keyword,))
                qr_res = qp.getFromTable('keyword', ('tag', keyword))
				qr_res = qr_res.project('id')
				qr_res = qr_res.sort('id')

            cur.execute("""INSERT INTO article_keyword(article_id, keyword_id)
                VALUES (%s, %s)""", (id, keyword_id))
            qp.addToTable('article_keyword', ('article_id', id), ('keyword_id', keyword_id))

                cur.execute("""INSERT INTO reference(from_id, to_id)
                    VALUES (%s, %s)""", (id, int(ref_to)))
				qp.addToTable('reference', ('from_id', id), ('to_id', int(ref_to)))

                cur.execute("""INSERT INTO reference(from_id, to_id)
                    VALUES (%s, %s)""", (id, int(ref_from)))
				qp.addToTable('reference', ('from_id', id), ('to_id', int(ref_from)))
"""============================================================
==============================================================="""

class ArticleDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""DELETE FROM article_author WHERE article_id=%s""", (id, ))
		qp.deleteFromTable('article_author', ('article_id', id))

        cur.execute("""DELETE FROM article_keyword WHERE article_id=%s""", (id, ))
		qp.deleteFromTable('article_keyword', ('article_id', id))

        cur.execute("""DELETE FROM reference WHERE from_id=%s OR to_id=%s""", (id, id))
		qp.deleteFromTable('reference', ('from_id', id), ('to_id', id))

        cur.execute("""DELETE FROM article WHERE id=%s""", (id, ))
		qp.deleteFromTable('article', ('id', id))

"""============================================================
==============================================================="""

class ArticleUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
		cur.execute("""SELECT * FROM article WHERE id=%s;""", (id, ))
		qr_res = qp.getFromTable('article', ('id', id))
		qr_res = qr_res.sort('id')

		cur.execute("""SELECT author.id,name FROM author, article_author
                           WHERE author_id=author.id AND  article_id=%s""", (id, ))
		qr_article_author = qp.getFromTable('article_author', ('article_id', id))
		qr_author = qp.getFromTable('author')
		qr_res = qr_author.join(qr_article_author, 'id', 'author_id')
		qr_res = qr_res.project('id', 'name')
		qr_res = qr_res.sort('id')

		cur.execute("""SELECT to_id, paper_title FROM reference, article WHERE article.id=to_id AND from_id=%s""", (id, ))
		qr_reference = qp.getFromTable('reference', ('from_id', id))
		qr_author = qp.getFromTable('article')
		qr_res = qr_reference.join(qr_article, 'id', 'to_id')
		qr_res = qr_res.project('to_id', 'paper_title')
		qr_res = qr_res.sort('to_id')

		cur.execute("""SELECT from_id, paper_title FROM reference, article WHERE article.id=from_id AND to_id=%s""", (id, ))
		qr_reference = qp.getFromTable('reference', ('to_id', id))
		qr_author = qp.getFromTable('article')
		qr_res = qr_reference.join(qr_article, 'id', 'from_id')
		qr_res = qr_res.project('to_id', 'paper_title')
		qr_res = qr_res.sort('to_id')

		cur.execute("""SELECT tag FROM keyword, article_keyword
                            WHERE article_id=%s AND keyword_id=keyword.id""", (id, ))
		qr_article_keyword = qp.getFromTable('article_keyword', ('article_id', id))
		qr_author = qp.getFromTable('article')
		qr_res = qr_keyword.join(qr_article_keyword, 'id', 'keyword_id')
		qr_res = qr_res.project('tag')
		qr_res = qr_res.sort('tag')
"""============================================================
==============================================================="""

class ArticleUpdateSaveHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""UPDATE article SET id=%s, paper_title=%s, year=%s, venue=%s
            WHERE id=%s""", (id, title, year, venue, id))
		qp.deleteFromTable('article', ('id', id))
		qp.addToTable('author', ('id', id), ('paper_title', paper_title), ('year', year), ('venue', venue))

"""============================================================
==============================================================="""

class ArticleUpdateAddAuthorHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""SELECT id FROM author WHERE name=%s""", (name, ))
		qr_author = qp.getFromTable('author', ('name', name))
		qr_res = qr_res.project('id')
		qr_res = qr_res.sort('id')

		cur.execute("""INSERT INTO author(name, institute) VALUES
                (%s, %s)""", (name, "NULL"))
		qp.addToTable('author', ('name', name), ('institute', "NULL"))

		cur.execute("""SELECT author_id  author WHERE author.name=%s""", (name, ))
		qr_author = qp.getFromTable('author', ('name', name))
		qr_res = qr_res.project('author_id')
		qr_res = qr_res.sort('author_id')

		cur.execute("""INSERT INTO article_author (author_id, article_id)
                VALUES (%s, %s)""", (author_id[0], id))
		qp.addToTable('article_author', ('author_id', author_id[0]), ('article_id', id))
"""============================================================
==============================================================="""

class ArticleUpdateDeleteAuthorHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""DELETE FROM article_author
            WHERE author_id=%s AND article_id=%s""", (author_id, id))
		qp.deleteFromTable('article_author', ('author_id', author_id), ('id', id))

"""============================================================
==============================================================="""

class ArticleUpdateAddKeywordHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
	cur.execute("""SELECT id FROM keyword WHERE tag=%s""", (tag, ))
	qr_keyword = qp.getFromTable('keyword', ('tag', tag))
	qr_res = qr_res.project('id')
	qr_res = qr_res.sort('id')

	cur.execute("""INSERT INTO keyword(tag) VALUES
                    (%s)""", (tag, ))
	qp.addToTable('keyword', ('tag', tag))

	cur.execute("""SELECT id FROM keyword WHERE tag=%s""", (tag, ))
	qr_keyword = qp.getFromTable('keyword', ('tag', tag))
	qr_res = qr_res.project('id')
	qr_res = qr_res.sort('id')

	cur.execute("""INSERT INTO article_keyword (article_id, keyword_id)
                    VALUES (%s, %s)""", (id, tag_id[0]))
	qp.addToTable('article_keyword', ('article_id', id), ('keyword_id', keyword_id))

"""============================================================
==============================================================="""

class ArticleUpdateDeleteKeywordHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""SELECT id FROM keyword WHERE tag=%s""", (tag, ))
		qr_keyword = qp.getFromTable('keyword', ('tag', tag))
		qr_res = qr_res.project('id')
		qr_res = qr_res.sort('id')

		cur.execute("""DELETE FROM article_keyword
            WHERE keyword_id=%s AND article_id=%s""", (keyword_id, id))
		qp.deleteFromTable('article_keyword', ('keyword_id', keyword_id), ('article_id', id))
"""============================================================
==============================================================="""

class ArticleUpdateAddReftoHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        cur.execute("""INSERT INTO reference (from_id, to_id)
            VALUES (%s, %s)""", (id, article_id))
		qp.addToTable('reference', ('from_id', id), ('to_id', article_id))
"""============================================================
==============================================================="""


class ArticleUpdateDeleteReftoHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""DELETE FROM reference
            WHERE from_id=%s AND to_id=%s""", (id, article_id))
		qp.deleteFromTable('reference', ('from_id', id), ('to_id', article_id))
"""============================================================
==============================================================="""

class ArticleUpdateAddReffromHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""INSERT INTO reference (from_id, to_id)
            VALUES (%s, %s)""", (article_id, id))
		qp.addToTable('reference', ('from_id', article_id), ('to_id', id))
"""============================================================
==============================================================="""

class ArticleUpdateDeleteReffromHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
		cur.execute("""DELETE FROM reference
            WHERE from_id=%s AND to_id=%s""", (id, article_id))
		qp.deleteFromTable('reference', ('from_id', id), ('to_id', article_id))
