from btree import BPlusTree
import settings

class DataType:
    INTEGER = 1
    STRING = 2


class TableException(Exception):
    pass

class Table:
    def __init__(self, name):
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
    def delete(self, colname, val):
        indexesToDelete = self.get(colname, val).copy()
        for column in self.colIndexes.values():
            for values in column.values():
                values -= indexesToDelete

    #delete, than add
    def update(self, colname, val, newdata):
        pass

    #get from index, find, return
    #str colname, val
    def get(self, colname, val):
        #check schema
        if colname not in self.colIndexes:
            raise TableException('Table.get: Wrong column name \'' + colname +
                '\' or column is not searchable.')
        if self.colTypes[colname] == DataType.INTEGER:
            if not isinstance(val, int):
                raise TableException('Table.get: Wrong column type \'' + colname +
                    '\' INTEGER is expected.')
        elif self.colTypes[colname] == DataType.STRING:
            if not isinstance(val, str):
                raise TableException('Table.get: Wrong column type \'' + colname +
                    '\' STRING is expected.')

        if val in self.colIndexes[colname]:
            return self.colIndexes[colname][val]
        else:
            return set()

    #serialize
    def toData(self):
        pass

    #deserialize
    def fromData(self):
        pass
