import pickle

from buffermanager import *
from table import *

class QuerryProcessorException(Exception):
    pass

class QuerryProcessor:
    def __init__(self, filename=settings.filename):
        self.bufferManager = BufferManager(filename)
        self.tables = {}

    #columns - tuples (colname, datatype, isSearchable)
    def createTable(self, tableName, *columns):
        if (tableName in self.tables):
            raise QuerryProcessorException('Table ' + tableName + ' already exists')
        self.tables[tableName] = Table(tableName)
        for col in columns:
            self.tables[tableName].addColumn(col[0], col[1], col[2])

    def loadTables(self):
        self.tables = pickle.loads(self.bufferManager.loadMetaData())

    def saveTables(self):
        self.bufferManager.saveMetaData(pickle.dumps(self.tables))

    def getFromTable(self, tableName, *values):
        if tableName not in self.tables:
            raise QuerryProcessorException('There is no table \'' + tableName +
                '\'.')
        res = []
        for entry in self.tables[tableName].get(*values):
            res.append(pickle.loads(self.bufferManager.readData(entry)))
        return res

    #table name, [column name, value]
    def addToTable(self, tableName, *values):
        if tableName not in self.tables:
            raise QuerryProcessorException('There is no table \'' + tableName +
                '\'.')
        data = []
        for val in values:
            data.append(val[1])
        entry = self.bufferManager.writeData(pickle.dumps(data))
        self.tables[tableName].add(entry, *values)

    def deleteFromTable(self, tableName, *values):
        if tableName not in self.tables:
            raise QuerryProcessorException('There is no table \'' + tableName +
                '\'.')
        self.tables[tableName].delete(*values)
