import unittest

from buffermanager import BufferManager
from dataentry import DataEntry
from page import Page

class TestBufferManager(unittest.TestCase):
    def setUp(self):
        open('test/testData/test_db.data', 'w').close()
        self.bm = BufferManager('test/testData/test_db.data')
        self.bm.buffersize = 3

    def tearDown(self):
        del self.bm

    @unittest.skip
    def testWriteData(self):
        for i in range(0, 1000):
            entry = self.bm.writeData(b'1 2 3 4')
            print(str(entry.page) + " " + str(entry.offset))
            entry = self.bm.writeData(b'uno dos tres cuatro')
            print(str(entry.page) + " " + str(entry.offset))
            entry = self.bm.writeData(b'one two three four')
            print(str(entry.page) + " " + str(entry.offset))

        print(self.bm.readData(DataEntry(11, 1152)))
        print(self.bm.readData(DataEntry(17, 1473)))

    def testSaveLoadMetadata(self):
        self.bm.lastEmptyPage = 42
        mdstr = b'Quick red fox jump over lazy dog'
        self.bm.saveMetaData(mdstr)
        self.assertEqual(self.bm.lastEmptyPage, 42)
        self.bm.lastEmptyPage = 54
        md = self.bm.loadMetaData()
        self.assertEqual(self.bm.lastEmptyPage, 42)
        self.assertEqual(md, mdstr)

if __name__ == '__main__':
    unittest.main()
