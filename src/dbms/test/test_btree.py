import random
import unittest

from btree import *

class BTreeTests(unittest.TestCase):
    def test_additions(self):
        bt = BTree(20)
        l = list(range(2000))
        for i, item in enumerate(l):
            bt.insert(item)
            self.assertEqual(list(bt), l[:i + 1])

    def test_bulkloads(self):
        bt = BTree.bulkload(list(range(2000)), 20)
        self.assertEqual(list(bt), list(range(2000)))

    def test_removals(self):
        bt = BTree(20)
        l = list(range(2000))
        list(map(bt.insert, l))
        rand = l[:]
        random.shuffle(rand)
        while l:
            self.assertEqual(list(bt), l)
            rem = rand.pop()
            l.remove(rem)
            bt.remove(rem)
        self.assertEqual(list(bt), l)

    def test_insert_regression(self):
        bt = BTree.bulkload(list(range(2000)), 50)

        for i in range(100000):
            bt.insert(random.randrange(2000))


class BPlusTreeTests(unittest.TestCase):
    def test_additions_sorted(self):
        bt = BPlusTree(20)
        l = list(range(2000))

        for item in l:
            bt.insert(item, str(item))

        for item in l:
            self.assertEqual(str(item), bt[item])

        self.assertEqual(l, list(bt))

    def test_additions_random(self):
        bt = BPlusTree(20)
        l = list(range(2000))
        random.shuffle(l)

        for item in l:
            bt.insert(item, str(item))

        for item in l:
            self.assertEqual(str(item), bt[item])

        self.assertEqual(list(range(2000)), list(bt))

    def test_bulkload(self):
        bt = BPlusTree.bulkload(list(zip(list(range(2000)), list(map(str, list(range(2000)))))), 20)

        self.assertEqual(list(bt), list(range(2000)))

        self.assertEqual(
                list(bt.items()),
                list(zip(list(range(2000)), list(map(str, list(range(2000)))))))


if __name__ == '__main__':
    unittest.main()
