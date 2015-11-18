from page import Page
import settings

class DiskManagerException(Exception):
    pass

class DiskManager:
    def __init__(self, filename=settings.filename):
        self.f = open(filename, 'r+b')

    def writePage(self, page): #pageNum, data):
        if len(bytes(page.data)) > settings.pagesize:
            raise DiskManagerException("Page size is not enough")
        self.f.seek(page.id * settings.pagesize)
        self.f.write(page.data)

    def readPage(self, pageNum):
        self.f.seek(pageNum * settings.pagesize)
        return Page(pageNum, self.f.read(settings.pagesize))

    def closeFile(self):
        self.f.close()
