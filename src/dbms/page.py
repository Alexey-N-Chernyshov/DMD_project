import struct
import time

from dataentry import DataEntry
import settings

class DiskManagerException(Exception):
    pass

# page struct in bytes:
# 2 - unsigned short - empty offset
# [further data - 2 - unsigned short - size of data - ? - data]

class Page:
    def __init__(self, id, data=b''):
        self.changed = True
        self.id = id
        if data:
            self.offsetEmpty = struct.unpack('H', data[0:2])[0]
            self.data = data[0:self.offsetEmpty]
        else:
            self.data = struct.pack('H', 2)
            self.offsetEmpty = 2
        self.time = time.time()

    def setOffsetEmpty(self, offset):
        self.offsetEmpty = offset
        self.data = struct.pack('H', offset) + self.data[2:]

    #append data if enough space
    #data - packed data
    #returns DataEntry of new data block
    def add(self, data):
        if self.getFreeSpace() < len(data) + 2:
            raise PageException('Page ' + str(self.id) + ': size is not enough')

        offset = self.offsetEmpty
        self.data += struct.pack('H', len(data))
        self.data += data
        self.setOffsetEmpty(self.offsetEmpty + len(data) + 2)

        return DataEntry(self.id, offset)

    #returns data at valid offset
    def get(self, offset):
        dataLen = struct.unpack('H', self.data[offset:offset + 2])[0]
        return self.data[offset + 2:offset + 2 + dataLen]

    #delete data. Consider offset is always valid.
    def delete(self, offset):
        dataLen = struct.unpack('H', self.data[offset:offset + 2])[0]
        self.data = self.data[:offset] + self.data[offset + dataLen + 2:]
        self.setOffsetEmpty(self.offsetEmpty - dataLen - 2)

    def getFreeSpace(self):
        return settings.pagesize - self.offsetEmpty
