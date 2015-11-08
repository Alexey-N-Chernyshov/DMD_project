import time

from diskmanager import DiskManager
import settings

class BufferManager:
    def __init__(self):
        self.diskManager = DiskManager(settings.filename)
        self.buffer = {}

    # loads page in buffer
    def loadPage(self, pageNum):
        page = self.buffer.get(pageNum)
        if page == None:
            page = self.diskManager.readPage(pageNum)
            if len(self.buffer) < settings.buffersize:
                self.buffer[page.id] = page
            else:
                removedPage = self.buffer.pop(min(self.buffer,
                        key = lambda p : self.buffer.get(p).time))
                if removedPage.changed:
                    self.diskManager.writePage(removedPage)
        else:
            page.time = time.time()

    def get(self, pageNum):
        self.loadPage(pageNum)
        return self.buffer.get(pageNum)

    def set(self, page):
        self.loadPage(page.id)
        page.changed = True
        page.time = time.time()
        self.buffer[page.id] = page

    # saves all changed pages on disk
    def commit(self):
        for p in self.buffer.values():
            if p.changed:
                self.diskManager.writePage(p)

if __name__ == '__main__':
    pass
    # b = BufferManager()
    # p = b.get(1)
    # print(str(p.id) + " " + str(p.time))
    # p = b.get(1)
    # print(str(p.id) + " " + str(p.time))
    # p = b.get(0)
    # print(str(p.id) + " " + str(p.time))
    #
    # for i in range(0, 100):
    #     b.get(i)
    #     b.get(1)
    #
    # for i in b.buffer.values():
    #     print(str(i.id) + ' ' + str(i.time))
    #
    # p = b.get(250)
    # p.data = b'data for 250 page'
    # b.set(p)
    # print(str(p.id) + " " + str(p.time))
    # b.commit()
