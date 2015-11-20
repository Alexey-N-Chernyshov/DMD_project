import pickle

from btree import BPlusTree
import settings

class DataType:
    INTEGER = 1
    STRING = 2


class TableException(Exception):
    pass

class Table:
    def __init__(self, name=''):
        self.name = name
        self.colTypes = {}
        self.colIndexes = {}

    #add column (name, type, is index)
    def addColumn(self, name, type, isSearchable):
        self.colTypes[name] = type
        if isSearchable:
            self.colIndexes[name] = {}
            #BPlusTree(settings.treeOrder)

    # add for all indecies and write to disk
    # entry - DataEntry
    # colData - tuples ('colname', value)
    def add(self, entry, *colData):
        #check schema
        if len(self.colTypes) != len(colData):
            raise TableException('Table.add: Wrong column number.')
        for d in colData:
            if d[0] not in self.colTypes:
                raise TableException('Table.add: Wrong column name \'' + d[0] + '\'')

        #add to indecies
        for d in colData:
            if d[0] in self.colIndexes:
                if d[1] not in self.colIndexes[d[0]]:
                    self.colIndexes[d[0]][d[1]] = set()
                    self.colIndexes[d[0]][d[1]].add(entry)
                else:
                    self.colIndexes[d[0]][d[1]].add(entry)

    # delete from indecies and from disk
    def delete(self, *colData):
        indexesToDelete = self.get(*colData).copy()
        for column in self.colIndexes.values():
            for values in column.values():
                values -= indexesToDelete

    #get from index, find, return
    #str colname, colData[1]
    def get(self, *colData):
        #check schema
        for col in colData:
            if col[0] not in self.colIndexes:
                raise TableException('Table.get: Wrong column name \''
                    + col[0] + '\' or column is not searchable.')
            if self.colTypes[col[0]] == DataType.INTEGER:
                if not isinstance(col[1], int):
                    raise TableException('Table.get: Wrong column type \''
                        + col[0] + '\' INTEGER is expected.')
            elif self.colTypes[col[0]] == DataType.STRING:
                if not isinstance(col[1], str):
                    raise TableException('Table.get: Wrong column type \''
                        + col[0] + '\' STRING is expected.')

        res = set()
        if colData[0][1] in self.colIndexes[colData[0][0]]:
            res = self.colIndexes[colData[0][0]][colData[0][1]]
        else:
            return set()
        for col in colData:
            if col[1] in self.colIndexes[col[0]]:
                res &= self.colIndexes[col[0]][col[1]]
        return res

    #serialize
    def toBytes(self):
        return pickle.dumps(self)

    #deserialize
    def fromBytes(self, data):
        return pickle.loads(data)
