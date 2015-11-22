import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import login

import psycopg2
import hashlib, binascii # for authentication

import Settings

from queryprocessor import *
from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)

conn = psycopg2.connect("dbname='" + Settings.db_name + "' user='"
    + Settings.db_username + "' host='" + Settings.db_host +"' password='" + Settings.db_password + "'")

dbfilename = 'test/testData/test_final_db.data' # default filename
qp = QueryProcessor(dbfilename)
qp.loadTables()

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.redirect(self.get_argument("next", u"/search/"))

#hadle search results. Displays all found articles in list
class SearchResultHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        title = self.get_argument('title')
        author = self.get_argument('author')
        venue = self.get_argument('venue')
        year = self.get_argument('year')
        keyword = self.get_argument('keyword')
        offset = self.get_argument('offset', 0)
        if int(offset) < 0:
            offset = 0

        order = self.get_argument('order', "by id def")
        print(order)

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

        cur = conn.cursor()
        cur.execute(query)
        articles = qr_res
        cur.close()

        self.render('searchresult.html', articles=articles, id=id, title=title,
            author=author, venue=venue, year=year, offset=offset, keyword=keyword, order=order)

class AuthorHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id')

        cur = conn.cursor()
        qr_author = qp.getFromTable('author', )
        qr_res = qp.getFromTable('author', ('id', id))
        qr_res = qr_res.project('id', 'name', 'institute')
        qr_res = qr_res.sort('id')
        author = qr_res[0]

        qr_article_author = qp.getFromTable('article_author', ('author_id', author_id))
        qr_article = qp.getFromTable('article')
        qr_res = qr_article_author.join(qr_article, 'article_id', 'id')
        qr_res = qr_res.project('article_id', 'paper_title')
        qr_res = qr_res.sort('article_id')
        articles = qr_res
        cur.close()

        self.render('author.html', id=author[0], name=author[1], institute=author[2], articles=articles)

class AuthorDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')

        cur = conn.cursor()
        qp.deleteFromTable('article_author', ('author_id', author_id))
        conn.commit()

        qp.deleteFromTable('author', ('id', id))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/search/"))

class AuthorUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id')

        cur = conn.cursor()
        qr_res = qp.getFromTable('author', ('id', id))
        qr_res = qr_res.project('id', 'name', 'institute')
        qr_res = qr_res.sort('id')
        author = qr_res[0]

        qr_article_author = qp.getFromTable('article_author', ('author_id', author_id))
        qr_article = qp.getFromTable('article')
        qr_res = qr_article_author.join(qr_article, 'article_id', 'id')
        qr_res = qr_res.project('article_id', 'paper_title')
        qr_res = qr_res.sort('article_id')
        articles = qr_res
        cur.close()

        self.render('authorupdate.html', id=author[0], name=author[1], institute=author[2], articles=articles)

class AuthorUpdateSaveHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        name = self.get_argument('name')
        institute = self.get_argument('institute')

        qp.deleteFromTable('author', ('id', id))
		qp.addToTable('author', ('id', id), ('name', name), ('institute', institute))

        self.redirect(self.get_argument("next", u"/author/?id=" + id))

class AuthorUpdateAddArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('article_id')

        qp.addToTable('article_author', ('id', id), ('article_id', article_id))

        self.redirect(self.get_argument("next", u"/author/update/?id=" + id))

class AuthorUpdateDeleteArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('article_id')

        qp.deleteFromTable('author', ('id', id), ('article_id', article_id))

        self.redirect(self.get_argument("next", u"/author/update/?id=" + id))

class ArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id')
        qr_article = qp.getFromTable('article',('id', id))
        article = qr_article[0][0]

        qr_article_author = qp.getFromTable('article_author', ('article_id', article_id))
		qr_author = qp.getFromTable('author')
		qr_res = qr_author.join(qr_article_author, 'id', 'article_id')
		qr_res = qr_res.project('id', 'name')
		qr_res = qr_res.sort('id')
        authors = qr_res

        qr_reference = qp.getFromTable('reference', ('from_id', id))
		qr_article = qp.getFromTable('article')
		qr_res = qr_reference.join(qr_article, 'to_id', 'id')
		qr_res = qr_res.project('to_id', 'paper_title')
		qr_res = qr_res.sort('to_id')
        tos = qr_res

        qr_reference = qp.getFromTable('reference', ('from_id', id))
		qr_article = qp.getFromTable('article')
		qr_res = qr_reference.join(qr_article, 'to_id', 'id')
		qr_res = qr_res.project('from_id', 'paper_title')
		qr_res = qr_res.sort('from_id')
        froms = qr_res

		qr_keyword = qp.getFromTable('keyword')
		qr_res = qr_keyword.join(qr_article_keyword, 'id', 'keyword_id')
		qr_res = qr_res.project('tag')
		qr_res = qr_res.sort('tag')
        keywords = qr_res

        cur.close()

        self.render('article.html', id=article[0], title=article[1], year=article[2],
            venue=article[3], authors=authors, tos=tos, froms=froms, keywords=keywords)

    def write_error(self, status_code, **kwargs):
        self.write("You caused a %d error." % status_code)

class SearchHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('search.html')

class AddArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('addarticle.html')

    def post(self):
        title = self.get_argument('title')
        authors = self.get_argument('author').split(",")
        venue = self.get_argument('venue')
        year = self.get_argument('year')
        keywords = self.get_argument('keyword').split(",")
        ref_tos = self.get_argument('ref_to').split(",")
        ref_froms = self.get_argument('ref_from').split(",")

        qr_res = qp.getFromTable('article')
		qr_res = qr_res.project('id')
		qr_res = qr_res.sort('id', reverse=True)
		qr_res = qr_res.limit(0, 1)
        id = qr_res[0][0]
        if id:
            id = id[0] + 1
        else:
            id = 0

        qp.addToTable('article', ('id', id), ('paper_title', title),('year', year) ,('venue', venue))

        for author in authors:
            qr_res = qp.getFromTable('author', ('name', author.strip()))
			qr_res = qr_res.project('id')
			qr_res = qr_res.sort('id')
            auth_id = qr_res[0][0]
            if not auth_id:
                qp.addToTable('author', ('name', name), ('institute', "NULL"))

                qr_res = qp.getFromTable('author', ('name', author))
				qr_res = qr_res.project('id')
				qr_res = qr_res.sort('id')
                auth_id = qr_res[0][0]

            qp.addToTable('article_author', ('article_id', id), ('author_id', auth_id))

        for keyword in keywords:
            keyword = keyword.strip()
            qr_res = qp.getFromTable('keyword', ('tag', keyword))
			qr_res = qr_res.project('id')
			qr_res = qr_res.sort('id')
            keyword_id = qr_res[0][0]
            if not keyword_id:
                qp.addToTable('keyword', ('tag', keyword))

                qr_res = qp.getFromTable('keyword', ('tag', keyword))
				qr_res = qr_res.project('id')
				qr_res = qr_res.sort('id')
                keyword_id = qr_res[0][0]

            qp.addToTable('article_keyword', ('article_id', id), ('keyword_id', keyword_id))

        for ref_to in ref_tos:
            if ref_to:
                qp.addToTable('reference', ('from_id', id), ('to_id', int(ref_to)))

        for ref_from in ref_froms:
            if ref_from:
                qp.addToTable('reference', ('from_id', id), ('to_id', int(ref_from)))

        self.redirect(self.get_argument("next", u"/article/?id=" + str(id)))

class ArticleDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')

        qp.deleteFromTable('article_author', ('article_id', id))

        qp.deleteFromTable('article_keyword', ('article_id', id))

        qp.deleteFromTable('reference', ('from_id', id), ('to_id', id))

        qp.deleteFromTable('article', ('id', id))

        self.redirect(self.get_argument("next", u"/search/"))

class ArticleUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id')
        qr_res = qp.getFromTable('article', ('id', id))
		qr_res = qr_res.sort('id')
        article = qr_res

        qr_article_author = qp.getFromTable('article_author', ('article_id', id))
		qr_author = qp.getFromTable('author')
		qr_res = qr_author.join(qr_article_author, 'id', 'author_id')
		qr_res = qr_res.project('id', 'name')
		qr_res = qr_res.sort('id')
        authors = qr_res

        qr_reference = qp.getFromTable('reference', ('from_id', id))
		qr_author = qp.getFromTable('article')
		qr_res = qr_reference.join(qr_article, 'id', 'to_id')
		qr_res = qr_res.project('to_id', 'paper_title')
		qr_res = qr_res.sort('to_id')
        tos = qr_res

        qr_reference = qp.getFromTable('reference', ('to_id', id))
		qr_author = qp.getFromTable('article')
		qr_res = qr_reference.join(qr_article, 'id', 'from_id')
		qr_res = qr_res.project('to_id', 'paper_title')
		qr_res = qr_res.sort('to_id')
        froms = qr_res

        qr_article_keyword = qp.getFromTable('article_keyword', ('article_id', id))
		qr_author = qp.getFromTable('article')
		qr_res = qr_keyword.join(qr_article_keyword, 'id', 'keyword_id')
		qr_res = qr_res.project('tag')
		qr_res = qr_res.sort('tag')

        keywords = qr_res

        self.render('articleupdate.html', id=article[0], title=article[1], year=article[2],
            venue=article[3], authors=authors, tos=tos, froms=froms, keywords=keywords)

class ArticleUpdateSaveHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        title = self.get_argument('title')
        year = self.get_argument('year')
        venue = self.get_argument('venue')

        qp.deleteFromTable('article', ('id', id))
		qp.addToTable('author', ('id', id), ('paper_title', paper_title), ('year', year), ('venue', venue))

        self.redirect(self.get_argument("next", u"/article/?id=" + id))

class ArticleUpdateAddAuthorHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        name = self.get_argument('name')

        qr_author = qp.getFromTable('author', ('name', name))
		qr_res = qr_res.project('id')
		qr_res = qr_res.sort('id')
        author_id = qr_res[0][0]

        if not author_id:
            qp.addToTable('author', ('name', name), ('institute', "NULL"))

            qr_author = qp.getFromTable('author', ('name', name))
    		qr_res = qr_res.project('author_id')
    		qr_res = qr_res.sort('author_id')

            author_id = qr_res[0][0]

        try:
            qp.addToTable('article_author', ('author_id', author_id[0]), ('article_id', id))
        except:
            pass

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateDeleteAuthorHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        author_id = self.get_argument('author_id')

        qp.deleteFromTable('article_author', ('author_id', author_id), ('id', id))

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateAddKeywordHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        tag = self.get_argument('tag')
        if tag:
            cur = conn.cursor()
            qr_keyword = qp.getFromTable('keyword', ('tag', tag))
        	qr_res = qr_res.project('id')
        	qr_res = qr_res.sort('id')
            tag_id = qr_res[0]
            if not tag_id:
                qp.addToTable('keyword', ('tag', tag))

                qr_keyword = qp.getFromTable('keyword', ('tag', tag))
            	qr_res = qr_res.project('id')
            	qr_res = qr_res.sort('id')
                tag_id = qr_res[0]

            try:
                qp.addToTable('article_keyword', ('article_id', id), ('keyword_id', keyword_id))
            except:
                pass

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateDeleteKeywordHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        tag = self.get_argument('tag')

        qp.deleteFromTable('article_keyword', ('keyword_id', keyword_id), ('article_id', id))

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateAddReftoHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('ref_to')

        qp.addToTable('reference', ('from_id', id), ('to_id', article_id))

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateDeleteReftoHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('ref_to')

        qp.deleteFromTable('reference', ('from_id', id), ('to_id', article_id))

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateAddReffromHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('ref_from')

        qp.addToTable('reference', ('from_id', article_id), ('to_id', id))

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateDeleteReffromHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('ref_from')

        qp.deleteFromTable('reference', ('from_id', id), ('to_id', article_id))

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class AuthSigninHandler(BaseHandler):
    def get(self):
        self.render("signin.html")

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")

        dk = hashlib.pbkdf2_hmac('sha256', bytearray(username, 'utf8'), b'salt', 100000)
        username_hashed = binascii.hexlify(dk).decode("ascii")
        dk = hashlib.pbkdf2_hmac('sha256', bytearray(password, 'utf8'), b'salt', 100000)
        password_hashed = binascii.hexlify(dk).decode("ascii")

        #get hash password from database
        try:
            login.get_hash_signin(username_hashed, password_hashed)
        except:
            self.render("signin.html")

        if True:
            self.redirect(self.get_argument("next", u"/auth/login/"))
        else:
            self.render("signin.html")

class AuthLoginHandler(BaseHandler):
    def get(self):
        try:
            errormessage = self.get_argument("error")
        except:
            errormessage = ""
        self.render("login.html", errormessage = errormessage)

    def check_permission(self, password, username):
        #get hash of name
        dk = hashlib.pbkdf2_hmac('sha256', bytearray(username, 'utf8'), b'salt', 100000)
        username_hashed = binascii.hexlify(dk).decode("ascii")

        #get hash password from database
        return login.get_hash_login(username_hashed, password)

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        auth = self.check_permission(password, username)
        if auth:
            self.set_current_user(username)
            self.redirect(self.get_argument("next", u"/search/"))
        else:
            error_msg = u"?error=" + tornado.escape.url_escape("Login incorrect")
            self.redirect(u"/auth/login/" + error_msg)

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")

class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/auth/signin/", AuthSigninHandler),
            (r"/auth/login/", AuthLoginHandler),
            (r"/auth/logout/", AuthLogoutHandler),
            (r"/search/", SearchHandler),
            (r'/article/', ArticleHandler),
            (r'/article/delete/', ArticleDeleteHandler),
            (r'/article/update/', ArticleUpdateHandler),
            (r'/article/update/save/', ArticleUpdateSaveHandler),
            (r'/article/update/addauthor/', ArticleUpdateAddAuthorHandler),
            (r'/article/update/deleteauthor/', ArticleUpdateDeleteAuthorHandler),
            (r'/article/update/addkeyword/', ArticleUpdateAddKeywordHandler),
            (r'/article/update/deletekeyword/', ArticleUpdateDeleteKeywordHandler),
            (r'/article/update/addrefto/', ArticleUpdateAddReftoHandler),
            (r'/article/update/deleterefto/', ArticleUpdateDeleteReftoHandler),
            (r'/article/update/addreffrom/', ArticleUpdateAddReffromHandler),
            (r'/article/update/deletereffrom/', ArticleUpdateDeleteReffromHandler),
            (r'/author/', AuthorHandler),
            (r'/author/delete/', AuthorDeleteHandler),
            (r'/author/update/', AuthorUpdateHandler),
            (r'/author/update/addarticle/', AuthorUpdateAddArticleHandler),
            (r'/author/update/deletearticle/', AuthorUpdateDeleteArticleHandler),
            (r'/author/update/save/', AuthorUpdateSaveHandler),
            (r'/searchresult/', SearchResultHandler),
            (r'/addarticle/', AddArticleHandler),
        ]
        settings = {
            "template_path":Settings.TEMPLATE_PATH,
            "static_path":Settings.STATIC_PATH,
            "debug":Settings.DEBUG,
            "cookie_secret": Settings.COOKIE_SECRET,
            "login_url": "/auth/login/"
        }
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
