from page import Page
import settings

class DiskManagerException(Exception):
    pass

class DiskManager:
    def __init__(self, filename=settings.filename):
        self.f = open(filename, 'r+b')

    def writePage(self, page):
        if len(bytes(page.data)) > settings.pagesize:
            raise DiskManagerException('Page ' + str(page.id) +
                ': size is not enough ' + str(len(bytes(page.data))))
        self.f.seek(page.id * settings.pagesize)
        self.f.write(page.data)

    def readPage(self, pageNum):
        self.f.seek(pageNum * settings.pagesize)
        return Page(pageNum, self.f.read(settings.pagesize))

    def closeFile(self):
        self.f.close()

    def writeDirect(self, data):
        pass
