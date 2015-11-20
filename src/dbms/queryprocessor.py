from table import *

class QuerryProcessorException(Exception):
    pass

class QuerryProcessor:
    def __init__(self):
        self.tables = {}

    #columns - tuples (colname, datatype, isSearchable)
    def createTable(self, tableName, *columns):
        if (tableName in self.tables):
            raise QuerryProcessorException('Table ' + tableName + ' already exists')
        self.tables[tableName] = Table()
        for col in columns:
            self.tables[tableName].addColumn(col[0], col[1], col[2])

    def loadTables(self):
        pass

    def saveTables(self):
        pass

    def getFromTable(self, name, colname, val):
        pass

    #table name, [column name, value]
    def addToTable(self, tableName):
        pass
