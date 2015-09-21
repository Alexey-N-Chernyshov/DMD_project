#!/usr/bin/env/python
# -*- coding: utf-8 -*-

import time

class Article:
    index = 0
    name = ''
    year = 0
    venue = ''
    author = []
    references = []
    abstract = ''

    def __init__(self):
        self.references = list()

    def setIndex(self, line):
        self.index = int(line[6:-1])

    def setName(self, line):
        self.name = line[2:-1].decode('cp866')

    def setAuthor(self, line):
        self.author = line[2:-1].decode('cp866').split(',')

    def setYear(self, line):
        self.year = int(line[2:-1])

    def setVenue(self, line):
        self.venue = line[2:-1].decode('cp866')

    def setReference(self, line):
        self.references.append(int(line[2:-1].decode('cp866')))

    def setAbstract(self, line):
        self.abstract = line[2:-1].decode('cp866')

    def tostring(self):
        return 'Article:' + \
            '\n\tindex: ' + str(self.index) + \
            '\n\tname: ' + self.name + \
            '\n\tyear: ' + str(self.year) + \
            '\n\tvenue: ' + self.venue + \
            '\n\tauthor:' + str(self.author) + \
            '\n\treferences: ' + str(self.references) + \
            '\n\tabstract: ' + self.abstract

if __name__ == '__main__':
    filename = '../../data/data.txt'

    startTime = time.time()
    countIndexes = 0
    countArticles = 0
    countReferences = 0
    maxAbstractLen = 0
    maxVenueLen = 0

    with open(filename, 'rb', 1) as infile:
        print('Open file ' + infile.name)
        a = Article()
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
                a.setAuthor(line)

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
                a.setAbstract(line)
                if len(a.abstract) > maxAbstractLen:
                    maxAbstractLen = len(a.abstract)

            if line == b'\n':
                #print(a.tostring())
                countArticles += 1
                if (countArticles % 1000) == 0:
                    print('Articles proceeded: ' + str(countArticles))
                    print('Reference count: ' + str(countReferences))
                    print('Max abstract length: ' + str(maxAbstractLen))
                    print('Max venue length: ' + str(maxVenueLen))
                    #if not a is None:
                    print(a.tostring())
                    print()
                a = Article()

    print('Work is over! Time: %.0ds' % (time.time() - startTime))
    print('Indexes proceeded: ' + str(countIndexes))
    print('Articles proceeded: ' + str(countArticles))
    print('Reference count: ' + str(countReferences))
    print('Max abstract length: ' + str(maxAbstractLen))
    print('Max venue length: ' + str(maxVenueLen))
