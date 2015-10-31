#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time
import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
import sys
from summa import keywords

#-------------------------------------------------------------------------------
filename = '../../data/data.txt' # default filename
startIndex = 0
extractKeywords = True#False
maxKeywordsFromArticle = 15      # how many keywords should be extracted

#-------------------------------------------------------------------------------
class Article:
    index = 0
    name = ''
    year = 0
    venue = ''
    authors = []
    references = []
    abstract = ''
    keywordsArticle = []

    def __init__(self):
        self.references = list()

    def setIndex(self, line):
        self.index = int(line[6:-1])

    def setName(self, line):
        self.name = line[2:-1].decode('cp866')

    def setAuthors(self, line):
        self.authors = line[2:-1].decode('cp866').split(',')

    def setYear(self, line):
        self.year = int(line[2:-1])

    def setVenue(self, line):
        self.venue = line[2:-1].decode('cp866')

    def setReference(self, line):
        self.references.append(int(line[2:-1].decode('cp866')))

    def setAbstract(self, line):
        text = line[2:-1]
        if len(text) > 0:
            self.abstract = text.decode('cp866')
            if extractKeywords:
                try:
                    self.keywordsArticle = keywords.keywords(text).split('\n')[0:maxKeywordsFromArticle]
                    return 0
                except Exception as e:
                    print('Exception while extracting keywords from article id: ' +\
                        str(self.index) + ' ' + str(e))
                    print('Abstract: ' + self.abstract)
                    return -1

    def tostring(self):
        return 'Article:' + \
            '\n\tindex: ' + str(self.index) + \
            '\n\tname: ' + self.name + \
            '\n\tyear: ' + str(self.year) + \
            '\n\tvenue: ' + self.venue + \
            '\n\tauthor:' + str(self.author) + \
            '\n\treferences: ' + str(self.references) + \
            '\n\tabstract: ' + self.abstract

def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Database file', default=filename)
    parser.add_argument('-i', '--index', help='Start from index', default=startIndex)
    return parser

if __name__ == '__main__':
    #statistics
    startTime = time.time()
    countIndexes = 0
    countArticles = 0
    countReferences = 0
    countHasAbstract = 0
    maxAbstractLen = 0
    maxVenueLen = 0
    maxKeywordsArticle = 0
    countAllKeywords = 0        # counts all keywords from all articles (non-unique)
    countAbstractExceptions = 0
    doesAbstractParse = True   # set True for parsing abstracts

    #parse args
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    filename = namespace.file
    startIndex = int(namespace.index)

    #Define our connection string
    conn_string = "host='localhost' dbname='dmd_project' user='postgres' password='postgres'"
    # print the connection string we will use to connect
    print("Connecting to database\n	->%s" % (conn_string))
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)
    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()
    print("Connected!\n")

    with open(filename, 'rb', 1) as infile:
        print('Open file ' + infile.name)
        a = Article()
        infile.readline() # skip first line
        for line in infile:
            # #index starts article index
            if line.startswith(b'#index'):
                a.setIndex(line)
                countIndexes += 1

            # #* starts article name
            if line.startswith(b'#*'):
                a.setName(line)

            # #@ starts article author
            if line.startswith(b'#@'):
                a.setAuthors(line)

            # #t starts article year
            if line.startswith(b'#t'):
                a.setYear(line)

            # #c starts article venue
            if line.startswith(b'#c'):
                a.setVenue(line)
                if len(a.venue) > maxVenueLen:
                    maxVenueLen = len(a.venue)

            # #% starts article reference
            if line.startswith(b'#%'):
                a.setReference(line)
                countReferences += 1

            # #a starts article abstract
            if line.startswith(b'#!'):
                if a.index >= startIndex:
                    if doesAbstractParse:
                        if a.setAbstract(line) == -1:
                            countAbstractExceptions += 1
                            print('Abstract total: ' + str(countHasAbstract))
                            print('Abstract error: ' + str(countAbstractExceptions))
                        if len(a.abstract) > maxAbstractLen:
                            maxAbstractLen = len(a.abstract)
                        if len(a.abstract) > 0:
                            countHasAbstract += 1
                        countAllKeywords += len(a.keywordsArticle)
                        if len(a.keywordsArticle) > maxKeywordsArticle:
                            maxKeywordsArticle = len(a.keywordsArticle)

            #article has been read
            if line == b'\n':
                countArticles += 1
                if a.index >= startIndex:
                    #insert article into db
                    try:
                        cursor.execute("INSERT INTO article(id, paper_title, year, venue) VALUES (%s, %s, %s, %s)", (str(a.index), a.name.encode("utf8"), str(a.year), a.venue.encode("utf8")))
                        conn.commit()
                    except (psycopg2.IntegrityError, psycopg2.InternalError) as exc:
                        print("Smth get wrong, but ok... ", exc)
                        conn.rollback()

                    #insert authors
                    for author in a.authors:
                        try:
                            cursor.execute("INSERT INTO author(name, institute) VALUES (%s, %s)", (author.encode("utf8"), "NULL"))
                            conn.commit()
                        except (psycopg2.IntegrityError, psycopg2.InternalError) as exc:
                            print("Smth get wrong, but ok... ", exc)
                            conn.rollback()

                        #insert article_author references
                        try:
                            cursor.execute("SELECT id FROM author WHERE name = %s LIMIT 1", (author.encode("utf8"), ))
                            row = cursor.fetchone()
                            authorId = row[0]
                            cursor.execute("INSERT INTO article_author(article_id, author_id) VALUES (%s, %s)", (a.index, authorId))
                        except (psycopg2.IntegrityError, psycopg2.InternalError) as exc:
                            print("Smth get wrong, but ok... ", exc)
                            conn.rollback()

                    #insert keywords
                    for keyword in a.keywordsArticle:
                        try:
                            cursor.execute("INSERT INTO keyword(tag) VALUES (%s)", (keyword, ))
                            conn.commit()
                        except (psycopg2.IntegrityError, psycopg2.InternalError) as exc:
                            print("Smth get wrong, but ok... ", exc)
                            conn.rollback()

                        #insert article_keyword references
                        try:
                            cursor.execute("SELECT id FROM keyword WHERE tag = %s LIMIT 1", (keyword, ))
                            row = cursor.fetchone()
                            keywordId = row[0]
                            cursor.execute("INSERT INTO article_keyword(article_id, keyword_id) VALUES (%s, %s)", (a.index, keywordId))
                        except (psycopg2.IntegrityError, psycopg2.InternalError) as exc:
                            print("Smth get wrong, but ok... ", exc)
                            conn.rollback()

                    for ref in a.references:
                        try:
                            cursor.execute("INSERT INTO reference(from_id, to_id) VALUES (%s, %s)", (a.index, ref))
                            conn.commit()
                        except (psycopg2.IntegrityError, psycopg2.InternalError) as exc:
                            print("Smth get wrong, but ok... ", exc)
                            conn.rollback()

                if (countArticles % 10000) == 0:
                    print('----------------------------------------------------')
                    print('Estimate time: %0.ds' % (time.time() - startTime))
                    print('Articles proceeded: ' + str(countArticles))
                    print('Reference count: ' + str(countReferences))
                    print('Max abstract length: ' + str(maxAbstractLen))
                    print('Max venue length: ' + str(maxVenueLen))
                a = Article()

    print('Work is over! Time: %0.ds' % (time.time() - startTime))
    print('Indexes proceeded: ' + str(countIndexes))
    print('Articles proceeded: ' + str(countArticles))
    print('Reference count: ' + str(countReferences))
    print('Abstarct proceeded: ' + str(countHasAbstract))
    print('Max abstract length: ' + str(maxAbstractLen))
    print('Max venue length: ' + str(maxVenueLen))
    print('Max keywords in one article: ' + str(maxKeywordsArticle))
    print('Total keywords in all articles: ' + str(countAllKeywords))
    print('Total exceptions while extracting keywords: ' + str(countAbstractExceptions))
