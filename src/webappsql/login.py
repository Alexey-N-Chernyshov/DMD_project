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

#get hash password from database
def get_hash_signin(username_hashed, password_hashed):
	conn_auth = psycopg2.connect("dbname='" + Settings.auth_db_name +
		"' user='" + Settings.auth_db_username + "' host='" +
		Settings.auth_db_host +"' password='" + Settings.auth_db_password + "'")
	cur_auth = conn_auth.cursor()
	cur_auth.execute("""INSERT INTO auth (login, pass) VALUES (%s, %s);""", (username_hashed, password_hashed))
	conn_auth.commit()
	cur_auth.close()
	conn_auth.close()

#get hash password from database
def get_hash_login(username_hashed, password):
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
	
def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
