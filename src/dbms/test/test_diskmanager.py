import unittest

from diskmanager import DiskManager
from page import Page

class TestDiskManager(unittest.TestCase):
    def setUp(self):
        open('test/testData/test_db.data', 'w').close()
        self.dm = DiskManager('test/testData/test_db.data')

    def tearDown(self):
        self.dm.closeFile()

    def testWrongFile(self):
        with self.assertRaises(IOError):
            DiskManager('/testData/wrong_filename.data')

    def testReadEmpty(self):
        page = self.dm.readPage(42)
        self.assertEqual(page.id, 42)
        self.assertTrue(page.data)

    def testWriteRead(self):
        for i in range(0, 100):
            data = bytes('page '.encode('utf8') + str(i).encode('utf8') + ' data\n'.encode('utf8'))
            page = Page(i, data)
            self.dm.writePage(page)
            page = self.dm.readPage(i)
            self.assertEqual(page.id, i)
            self.assertEqual(page.data, data)

if __name__ == '__main__':
    unittest.main()
