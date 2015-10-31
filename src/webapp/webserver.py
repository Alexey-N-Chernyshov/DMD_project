import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import psycopg2
import hashlib, binascii # for authentication

import Settings

from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)

conn = psycopg2.connect("dbname='" + Settings.db_name + "' user='"
    + Settings.db_username + "' host='" + Settings.db_host +"' password='" + Settings.db_password + "'")

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

        query = """SELECT article.id, paper_title, venue, year FROM
            article LEFT OUTER JOIN article_author ON article.id = article_author.article_id
            LEFT OUTER JOIN article_keyword ON article_keyword.article_id=article.id
            LEFT OUTER JOIN keyword ON keyword_id=keyword.id
            LEFT OUTER JOIN author ON author_id=author.id
            WHERE TRUE"""
        if id:
            query += ' AND article.id=' + id
        if title:
            query += ' AND paper_title=' + title
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

        cur = conn.cursor()
        cur.execute(query)
        articles = cur.fetchall()
        cur.close()

        self.render('searchresult.html', articles=articles, id=id, title=title,
            author=author, venue=venue, year=year, offset=offset, keyword=keyword, order=order)

class AuthorHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id')

        cur = conn.cursor()
        cur.execute("""SELECT id, name, institute FROM author WHERE id=%s;""", (id, ))
        author = cur.fetchone()

        cur.execute("""SELECT article_id, article.paper_title
            FROM article_author JOIN article ON article_id=article.id
            WHERE author_id=%s""",
            (id,))
        articles = cur.fetchall()
        cur.close()

        self.render('author.html', id=author[0], name=author[1], institute=author[2], articles=articles)

class AuthorDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')

        cur = conn.cursor()
        cur.execute("""DELETE FROM article_author WHERE author_id=%s""", (id, ))
        conn.commit()

        cur.execute("""DELETE FROM author WHERE id=%s""", (id, ))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/search/"))

class AuthorUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id')

        cur = conn.cursor()
        cur.execute("""SELECT id, name, institute FROM author WHERE id=%s;""", (id, ))
        author = cur.fetchone()

        cur.execute("""SELECT article_id, article.paper_title
            FROM article_author JOIN article ON article_id=article.id
            WHERE author_id=%s""",
            (id,))
        articles = cur.fetchall()
        cur.close()

        self.render('authorupdate.html', id=author[0], name=author[1], institute=author[2], articles=articles)

class AuthorUpdateSaveHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        name = self.get_argument('name')
        institute = self.get_argument('institute')

        cur = conn.cursor()
        cur.execute("""UPDATE author SET id=%s, name=%s, institute=%s
            WHERE id=%s""", (id, name, institute, id))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/author/?id=" + id))

class AuthorUpdateAddArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('article_id')

        cur = conn.cursor()
        cur.execute("""INSERT INTO article_author (author_id, article_id)
            VALUES (%s, %s)""", (id, article_id))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/author/update/?id=" + id))

class AuthorUpdateDeleteArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('article_id')

        cur = conn.cursor()
        cur.execute("""DELETE FROM article_author
            WHERE author_id=%s AND article_id=%s""", (id, article_id))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/author/update/?id=" + id))

class ArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id')
        cur = conn.cursor()
        cur.execute("""SELECT * FROM article WHERE id=%s;""", (id, ))
        article = cur.fetchone()

        cur.execute("""SELECT author.id,name FROM author, article_author
                           WHERE author_id=author.id AND  article_id=%s""", (id, ))
        authors = cur.fetchall()

        cur.execute("""SELECT to_id, paper_title FROM reference, article WHERE article.id=to_id AND from_id=%s""", (id, ))
        tos = cur.fetchall()

        cur.execute("""SELECT from_id, paper_title FROM reference, article WHERE article.id=from_id AND to_id=%s""", (id, ))
        froms = cur.fetchall()

        cur.execute("""SELECT tag FROM keyword, article_keyword
                            WHERE article_id=%s AND keyword_id=keyword.id""", (id, ))
        keywords = cur.fetchall()

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

        cur = conn.cursor()
        cur.execute("""SELECT id FROM article ORDER BY id DESC LIMIT 1""")
        id = cur.fetchone()
        if id:
            id = id[0] + 1
        else:
            id = 0

        cur.execute("""INSERT INTO article(id, paper_title, year, venue)
            VALUES (%s, %s, %s, %s);""", (id, title, year, venue))
        conn.commit()

        for author in authors:
            cur.execute("""SELECT id from author WHERE name=%s""", (author.strip(),))
            auth_id = cur.fetchone()
            if not auth_id:
                cur.execute("""INSERT INTO author(name, institute)
                    VALUES (%s, %s)""", (author, "NULL"))
                conn.commit()
                cur.execute("""SELECT id from author WHERE name=%s""", (author,))
                auth_id = cur.fetchone()

            cur.execute("""INSERT INTO article_author(article_id, author_id)
                VALUES (%s, %s)""", (id, auth_id))
            conn.commit()

        for keyword in keywords:
            keyword = keyword.strip()
            cur.execute("""SELECT id from keyword WHERE tag=%s""", (keyword,))
            keyword_id = cur.fetchone()
            if not keyword_id:
                cur.execute("""INSERT INTO keyword(tag)
                    VALUES (%s)""", (keyword, ))
                conn.commit()
                cur.execute("""SELECT id from keyword WHERE tag=%s""", (keyword,))
                keyword_id = cur.fetchone()

            cur.execute("""INSERT INTO article_keyword(article_id, keyword_id)
                VALUES (%s, %s)""", (id, keyword_id))
            conn.commit()

        for ref_to in ref_tos:
            if ref_to:
                cur.execute("""INSERT INTO reference(from_id, to_id)
                    VALUES (%s, %s)""", (id, int(ref_to)))
                conn.commit()

        for ref_from in ref_froms:
            if ref_from:
                cur.execute("""INSERT INTO reference(from_id, to_id)
                    VALUES (%s, %s)""", (int(ref_from), id))
                conn.commit()

        cur.close()

        self.redirect(self.get_argument("next", u"/article/?id=" + str(id)))

class ArticleDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')

        cur = conn.cursor()
        cur.execute("""DELETE FROM article_author WHERE article_id=%s""", (id, ))
        conn.commit()

        cur.execute("""DELETE FROM article_keyword WHERE article_id=%s""", (id, ))
        conn.commit()

        cur.execute("""DELETE FROM reference WHERE from_id=%s OR to_id=%s""", (id, id))
        conn.commit()

        cur.execute("""DELETE FROM article WHERE id=%s""", (id, ))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/search/"))

class ArticleUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id')
        cur = conn.cursor()
        cur.execute("""SELECT * FROM article WHERE id=%s;""", (id, ))
        article = cur.fetchone()

        cur.execute("""SELECT author.id,name FROM author, article_author
                           WHERE author_id=author.id AND  article_id=%s""", (id, ))
        authors = cur.fetchall()

        cur.execute("""SELECT to_id, paper_title FROM reference, article WHERE article.id=to_id AND from_id=%s""", (id, ))
        tos = cur.fetchall()

        cur.execute("""SELECT from_id, paper_title FROM reference, article WHERE article.id=from_id AND to_id=%s""", (id, ))
        froms = cur.fetchall()

        cur.execute("""SELECT tag FROM keyword, article_keyword
                            WHERE article_id=%s AND keyword_id=keyword.id""", (id, ))
        keywords = cur.fetchall()

        cur.close()

        self.render('articleupdate.html', id=article[0], title=article[1], year=article[2],
            venue=article[3], authors=authors, tos=tos, froms=froms, keywords=keywords)

class ArticleUpdateSaveHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        title = self.get_argument('title')
        year = self.get_argument('year')
        venue = self.get_argument('venue')

        cur = conn.cursor()
        cur.execute("""UPDATE article SET id=%s, paper_title=%s, year=%s, venue=%s
            WHERE id=%s""", (id, title, year, venue, id))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/article/?id=" + id))

class ArticleUpdateAddAuthorHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        name = self.get_argument('name')

        cur = conn.cursor()
        cur.execute("""SELECT id FROM author WHERE name=%s""", (name, ))
        author_id = cur.fetchone()
        if not author_id:
            cur.execute("""INSERT INTO author(name, institute) VALUES
                (%s, %s)""", (name, "NULL"))
            conn.commit()
            cur.execute("""SELECT author_id  author WHERE author.name=%s""", (name, ))
            author_id = cur.fetchone()

        try:
            cur.execute("""INSERT INTO article_author (author_id, article_id)
                VALUES (%s, %s)""", (author_id[0], id))
            conn.commit()
        except:
            conn.rollback()
        cur.close()

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateDeleteAuthorHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        author_id = self.get_argument('author_id')

        cur = conn.cursor()
        cur.execute("""DELETE FROM article_author
            WHERE author_id=%s AND article_id=%s""", (author_id, id))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateAddKeywordHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        tag = self.get_argument('tag')
        if tag:
            cur = conn.cursor()
            cur.execute("""SELECT id FROM keyword WHERE tag=%s""", (tag, ))
            tag_id = cur.fetchone()
            if not tag_id:
                cur.execute("""INSERT INTO keyword(tag) VALUES
                    (%s)""", (tag, ))
                conn.commit()
                cur.execute("""SELECT id FROM keyword WHERE tag=%s""", (tag, ))
                tag_id = cur.fetchone()

            try:
                cur.execute("""INSERT INTO article_keyword (article_id, keyword_id)
                    VALUES (%s, %s)""", (id, tag_id[0]))
                conn.commit()
            except:
                conn.rollback()
            cur.close()

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateDeleteKeywordHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        tag = self.get_argument('tag')

        cur = conn.cursor()
        cur.execute("""SELECT id FROM keyword WHERE tag=%s""", (tag, ))
        keyword_id = cur.fetchone()[0]
        cur.execute("""DELETE FROM article_keyword
            WHERE keyword_id=%s AND article_id=%s""", (keyword_id, id))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateAddReftoHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('ref_to')

        cur = conn.cursor()
        cur.execute("""INSERT INTO reference (from_id, to_id)
            VALUES (%s, %s)""", (id, article_id))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateDeleteReftoHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('ref_to')

        cur = conn.cursor()
        cur.execute("""DELETE FROM reference
            WHERE from_id=%s AND to_id=%s""", (id, article_id))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateAddReffromHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('ref_from')

        cur = conn.cursor()
        cur.execute("""INSERT INTO reference (from_id, to_id)
            VALUES (%s, %s)""", (article_id, id))
        conn.commit()
        cur.close()

        self.redirect(self.get_argument("next", u"/article/update/?id=" + id))

class ArticleUpdateDeleteReffromHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument('id')
        article_id = self.get_argument('ref_from')

        cur = conn.cursor()
        cur.execute("""DELETE FROM reference
            WHERE from_id=%s AND to_id=%s""", (id, article_id))
        conn.commit()
        cur.close()

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
            conn_auth = psycopg2.connect("dbname='" + Settings.auth_db_name +
                "' user='" + Settings.auth_db_username + "' host='" +
                Settings.auth_db_host +"' password='" + Settings.auth_db_password + "'")
            cur_auth = conn_auth.cursor()
            cur_auth.execute("""INSERT INTO auth (login, pass) VALUES (%s, %s);""", (username_hashed, password_hashed))
            conn_auth.commit()
            cur_auth.close()
            conn_auth.close()
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
        conn_auth = psycopg2.connect("dbname='" + Settings.auth_db_name +
            "' user='" + Settings.auth_db_username + "' host='" +
            Settings.auth_db_host +"' password='" + Settings.auth_db_password + "'")
        cur_auth = conn_auth.cursor()
        cur_auth.execute("""SELECT login, pass FROM auth WHERE login=%s;""", (str(username_hashed), ))
        auth_res = cur_auth.fetchone()
        if auth_res == None:
            cur_auth.close()
            conn_auth.close()
            return False
        password_hashed = auth_res[1]
        cur_auth.close()
        conn_auth.close()

        #hash incoming pass and compare
        dk = hashlib.pbkdf2_hmac('sha256', bytearray(password, 'utf8'), b'salt', 100000)
        if password_hashed == binascii.hexlify(dk).decode("ascii"):
            return True
        return False

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
