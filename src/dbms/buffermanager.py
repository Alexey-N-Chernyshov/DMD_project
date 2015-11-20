import time

from dataentry import DataEntry
from diskmanager import DiskManager
import settings

class BufferManager:
    def __init__(self, filename=settings.filename):
        self.diskManager = DiskManager(filename)
        self.buffer = {}
        self.lastEmptyPage = 0
        self.buffersize = settings.buffersize

    def __del__(self):
        self.commit()
        self.diskManager.closeFile()

    # loads page in buffer if it is not loaded
    def loadPage(self, pageNum):
        page = self.buffer.get(pageNum)
        if page == None:
            page = self.diskManager.readPage(pageNum)
            if len(self.buffer) >= self.buffersize:
                removedPage = self.buffer.pop(min(self.buffer,
                        key = lambda p : self.buffer.get(p).time))
                if removedPage.changed:
                    self.diskManager.writePage(removedPage)
            self.buffer[page.id] = page
        else:
            page.time = time.time()

    def getPage(self, pageNum):
        self.loadPage(pageNum)
        return self.buffer.get(pageNum)

    def setPage(self, page):
        self.loadPage(page.id)
        page.changed = True
        page.time = time.time()
        self.buffer[page.id] = page

    # saves all changed pages on disk
    def commit(self):
        for p in self.buffer.values():
            if p.changed:
                self.diskManager.writePage(p)

    #reads data by entry
    def readData(self, entry):
        page = self.getPage(entry.page)
        return page.get(entry.offset)

    #writes data to proper page and returns it's entry
    def writeData(self, data):
        page = self.getPage(self.lastEmptyPage)
        #empty space should be more then 30% of a pagesize (settings.pageFreeSpace)
        while page.getFreeSpace() - (len(data) + 2) < settings.pagesize * settings.pageFreeSpace:
            self.lastEmptyPage += 1
            page = self.getPage(self.lastEmptyPage)

        print('page is ' + str(self.lastEmptyPage))
        return page.add(data)

if __name__ == '__main__':
    pass