=============================================================
Installation.
1. install python 2.7 or 3.4 - the last versions will be fine

2. install tornado from any python packet manager
For example for windows
"C:\Python34\Lib\site-packages\easy_install.py" tornado
Use pip or pip3 for linux.

3. Postgresql must be installed.

4. install psycopg2
If you use windows DO NOT USE "pip3 install psycorp2"!!! There are some bugs.
Instead install it from http://www.stickpeople.com/projects/python/win-psycopg/
For linux users everything is fine.

=============================================================
(PHASE 2) HOW TO IMPORT SQL DB:
1. import dump (available at gdrive https://drive.google.com/file/d/0B7tof8A3zkr3X0xKVEdydXhGeHM/view?usp=sharing)
Command available both in Windows and Linux
psql -U username -f 'infile' database_name

2. execute query to add auth table to any database
src\sql\auth\create_auth.sql

3. configure Settings.py - set passwords, usernames, database connections

4. run web application src/webappsql/webserver.py

5. go to the http://localhost:8000

=============================================================
(PHASE 3) HOW TO IMPORT TO OUR DBMS FROM SQL DATABASE:
1. sql database to import must exists.

2. run src/dbms/psqlloader.py to create datafile for dbms and import data from Postgres

3. configure src/webapp/Settings.py

4. run web application src/webapp/webserver.py

5. go to the http://localhost:8000
