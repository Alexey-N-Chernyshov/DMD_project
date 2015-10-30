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

conn = psycopg2.connect("dbname='dmd_project' user='postgres' host='localhost' password='2qfksh4g'")

#hadle search results. Displays all found articles in list
class SearchResultHandler(tornado.web.RequestHandler):
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
            query += ' AND venue=' + venue
        if year:
            query += ' AND year=' + year
        if keyword:
           query += """ AND tag='""" + keyword + """'"""
        query += ' GROUP BY article.id OFFSET ' + str(offset)
        query += ' LIMIT 20'

        cur = conn.cursor()
        cur.execute(query)
        articles = cur.fetchall()
        cur.close()

        self.render('searchresult.html', articles=articles, id=id, title=title,
            author=author, venue=venue, year=year, offset=offset, keyword=keyword)

class ArticleHandler(tornado.web.RequestHandler):
    def get(self):
        id = self.get_argument('id')
        cur = conn.cursor()
        cur.execute("""SELECT * FROM article WHERE id=%s;""", (id, ))
        article = cur.fetchone()

        cur.execute("""SELECT name FROM author, article_author
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

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class SearchHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('search.html')


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
        conn_auth = psycopg2.connect("dbname='dmd_project' user='postgres' host='localhost' password='2qfksh4g'")
        cur_auth = conn_auth.cursor()
        cur_auth.execute("""INSERT INTO auth (login, pass) VALUES (%s, %s);""", (username_hashed, password_hashed))
        conn_auth.commit()
        cur_auth.close()
        conn_auth.close()

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
        conn_auth = psycopg2.connect("dbname='dmd_project' user='postgres' host='localhost' password='2qfksh4g'")
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
            (r"/search/", SearchHandler),
            (r"/auth/signin/", AuthSigninHandler),
            (r"/auth/login/", AuthLoginHandler),
            (r"/auth/logout/", AuthLogoutHandler),
            (r'/article', ArticleHandler),
            (r'/searchresult', SearchResultHandler),
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
