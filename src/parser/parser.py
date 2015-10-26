#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time
import sys
from summa import keywords

#-------------------------------------------------------------------------------
filename = '../../data/data.txt' # default filename
outFilename = 'out.txt'              # default output file
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
    parser.add_argument('-o', '--outfile', help='Output file', default=outFilename)
    return parser

if __name__ == '__main__':
    allKeywords = []
    allAuthors = []
    refAuthorArticle = []
    refArticleKeyword = []
    refArticleCite = []

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

    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    filename = namespace.file
    startIndex = int(namespace.index)
    outFilename = namespace.outfile
    outfile = open(outFilename, 'wb', 1)

    outfile.write('\nINSERT INTO article (id, paper_title, year, venue) VALUES\n')
    notWriteComma = True

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

            # #c starts article reference
            if line.startswith(b'#%'):
                a.setReference(line)
                countReferences += 1

            # #a starts article abstract
            if line.startswith(b'#!'):
                if a.index >= startIndex:
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

            if line == b'\n':
                #if a.index > startIndex:
                    #print(a.tostring())
                countArticles += 1

                for autor in a.authors:
                    if autor not in allAuthors:
                        allAuthors.append(autor)
                    refAuthorArticle.append((a.index, allAuthors.index(autor)))

                for keyword in a.keywordsArticle:
                    if keyword not in allKeywords:
                        allKeywords.append(keyword)
                    refArticleKeyword.append((a.index, allKeywords.index(keyword)))

                for ref in a.references:
                    refArticleCite.append((a.index, ref))

                if notWriteComma:
                    notWriteComma = False
                else:
                    outfile.write(',\n')
                venue = "NULL" if len(a.venue) == 0 else "'" + a.venue.encode("utf8") + "'"
                outfile.write("(" + str(a.index) + ", '" + a.name.encode("utf8") + "', " + str(a.year) + ", " + venue + ")")

                if (countArticles % 10000) == 0:
                    print('----------------------------------------------------')
                    print('Estimate time: %0.ds' % (time.time() - startTime))
                    print('Articles proceeded: ' + str(countArticles))
                    print('Reference count: ' + str(countReferences))
                    print('Max abstract length: ' + str(maxAbstractLen))
                    print('Max venue length: ' + str(maxVenueLen))
                    print('Total unique keywords: ' + str(len(allKeywords)))
                    print('Total keywords: ' + str(len(refArticleKeyword)))
                    print('Total unique authors: ' + str(len(allAuthors)))
                    print('Total authors: ' + str(len(refAuthorArticle)))
                    print('Total cites: ' + str(len(refArticleCite)))
                a = Article()

    outfile.write(';\n')
    outfile.write('\nINSERT INTO author (id, name, institute) VALUES\n')
    i = 0
    notWriteComma = True
    for author in allAuthors:
        if notWriteComma:
            notWriteComma = False
        else:
            outfile.write(',\n')
        outfile.write("(" + str(i) + ", '" + author.encode('utf8') + "', NULL)")
        i += 1

    outfile.write(';\n')
    notWriteComma = True
    outfile.write('\nINSERT INTO article_author (article_id, author_id) VALUES\n')
    for ref in refAuthorArticle:
        if notWriteComma:
            notWriteComma = False
        else:
            outfile.write(',\n')
        outfile.write('(' + str(ref[0]) + ', ' + str(ref[1]) + ')')

    i = 0
    outfile.write(';\n')
    notWriteComma = True
    outfile.write('\nINSERT INTO keyword (id, tag) VALUES\n')
    for keyword in allKeywords:
        if notWriteComma:
            notWriteComma = False
        else:
            outfile.write(',\n')
        outfile.write("(" + str(i) + ", '" + keyword.encode("utf8") + "')")
        i += 1

    outfile.write(';\n')
    notWriteComma = True
    outfile.write('\nINSERT INTO article_keyword (article_id, keyword_id) VALUES\n')
    for ref in refArticleKeyword:
        if notWriteComma:
            notWriteComma = False
        else:
            outfile.write(',\n')
        outfile.write('(' + str(ref[0]) + ', ' + str(ref[1]) + ')')

    outfile.write(';\n')
    notWriteComma = True
    outfile.write('\nINSERT INTO cite (from_id, to_id) VALUES\n')
    for ref in refArticleCite:
        if notWriteComma:
            notWriteComma = False
        else:
            outfile.write(',\n')
        outfile.write('(' + str(ref[0]) + ', ' + str(ref[1]) + ')')
    outfile.write(';\n')

    print('Work is over! Time: %0.ds' % (time.time() - startTime))
    print('Indexes proceeded: ' + str(countIndexes))
    print('Articles proceeded: ' + str(countArticles))
    print('Reference count: ' + str(countReferences))
    print('Abstarct proceeded: ' + str(countHasAbstract))
    print('Max abstract length: ' + str(maxAbstractLen))
    print('Max venue length: ' + str(maxVenueLen))
    print('Max keywords in one article: ' + str(maxKeywordsArticle))
    print('Total unique keywords count: ' + str(len(allKeywords)))
    print('Total keywords in all articles: ' + str(countAllKeywords))
    print('Total exceptions while extracting keywords: ' + str(countAbstractExceptions))
