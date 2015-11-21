import pickle

from buffermanager import *
from table import *

class QueryResultException(Exception):
    pass

class QueryResult:
    def __init__(self, columns, data):
        self.columns = columns
        self.data = data

    def join(self, other, columnSelf, columnOther):
        if columnSelf not in self.columns:
            raise QueryResultException('Wrong join field \'' + columnSelf + '\'')
        if columnOther not in other.columns:
            raise QueryResultException('Wrong join field \'' + columnOther + '\'')
        indSelf = self.columns.index(columnSelf)
        indOther = other.columns.index(columnOther)
        res = []
        for rSelf in self.data:
            for rOther in other.data:
                if rSelf[indSelf] == rOther[indOther]:
                    res.append(rSelf + rOther[:indOther] + rOther[indOther + 1:])

        return QueryResult(self.columns + other.columns[:indOther] +
            other.columns[indOther + 1:], res)

    def project(self, *columns):
        for col in columns:
            if col not in self.columns:
                raise QueryResultException('Wrong project field \'' + col + '\'')

        res = []
        for d in self.data:
            r = []
            for col in columns:
                r.append(d[self.columns.index(col)])
            res.append(r)

        return QueryResult(columns, res)

    def sort(self, column, reverse=False):
        if column not in self.columns:
            raise QueryResultException('Wrong sort field \'' + column + '\'')

        indCol = self.columns.index(column)
        return QueryResult(self.columns, sorted(self.data, key=lambda row : row[indCol], reverse=reverse))

    #function = tuple (resColName, function, (*colnames))
    def groupBy(self, *columns):
        for col in columns:
            if col not in self.columns:
                raise QueryResultException('Wrong groupBy field \'' + col + '\'')

        res = []
        resMult = {}
        for r in self.data:
            row = []
            for col in columns:
                row.append(r[self.columns.index(col)])
            if row not in res:
                res.append(row)

        return QueryResult(columns, res)

    def limit(self, fromInd, toInd):
        return QueryResult(self.columns, self.data[fromInd:toInd])

    def __iter__(self):
        return self.data.__iter__()

    def __next__(self):
        return self.data.__next__()


class QueryProcessorException(Exception):
    pass

class QueryProcessor:
    def __init__(self, filename=settings.filename):
        self.bufferManager = BufferManager(filename)
        self.tables = {}

    #columns - tuples (colname, datatype, isSearchable)
    def createTable(self, tableName, *columns):
        if (tableName in self.tables):
            raise QueryProcessorException('Table ' + tableName + ' already exists')
        self.tables[tableName] = Table(tableName)
        for col in columns:
            self.tables[tableName].addColumn(col[0], col[1], col[2])

    def loadTables(self):
        self.tables = pickle.loads(self.bufferManager.loadMetaData())

    def saveTables(self):
        self.bufferManager.saveMetaData(pickle.dumps(self.tables))

    def getFromTable(self, tableName, *values):
        if tableName not in self.tables:
            raise QueryProcessorException('There is no table \'' + tableName +
                '\'.')
        res = []
        for entry in self.tables[tableName].get(*values):
            res.append(pickle.loads(self.bufferManager.readData(entry)))
        return QueryResult(self.tables[tableName].columns, res)

    #table name, [column name, value]
    def addToTable(self, tableName, *values):
        if tableName not in self.tables:
            raise QueryProcessorException('There is no table \'' + tableName +
                '\'.')
        data = []
        for val in values:
            data.append(val[1])
        entry = self.bufferManager.writeData(pickle.dumps(data))
        self.tables[tableName].add(entry, *values)

    def deleteFromTable(self, tableName, *values):
        if tableName not in self.tables:
            raise QueryProcessorException('There is no table \'' + tableName +
                '\'.')
        self.tables[tableName].delete(*values)
