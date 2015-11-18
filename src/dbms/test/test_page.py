import unittest

from page import Page

class TestPage(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testEmptyPage(self):
        page = Page(12)
        self.assertEqual(page.id, 12)
        self.assertEqual(page.offsetEmpty, 2)

        page2 = Page(111, page.data)
        self.assertEqual(page2.id, 111)
        self.assertEqual(page2.offsetEmpty, 2)

    def testFreeSpace(self):
        page = Page(12)
        self.assertEqual(page.getFreeSpace(), 4094)

    def testAddData(self):
        page = Page(12)
        entry = page.add(b'123')
        self.assertEqual(entry.page, 12)
        self.assertEqual(entry.offset, 2)
        self.assertEqual(page.offsetEmpty, 7)

        entry = page.add(b'one two three')
        self.assertEqual(entry.page, 12)
        self.assertEqual(entry.offset, 7)
        self.assertEqual(page.offsetEmpty, 22)

        data = page.get(2)
        self.assertEqual(data, b'123')

        data = page.get(7)
        self.assertEqual(data, b'one two three')

if __name__ == '__main__':
    unittest.main()
