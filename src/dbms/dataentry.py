import settings

class DataEntry:
    def __init__(self, page, offset):
        self.page = page
        self.offset = offset

    def __eq__(self, other):
        if isinstance(other, DataEntry):
            return self.page == other.page and self.offset == other.offset
        return NotImplemented

    def __hash__(self):
        return self.offset + self.page * settings.pagesize

    def __str__(self):
        return 'Page: ' + str(self.page) + ' Offset: ' + str(self.offset)

    def __repr__(self):
        return 'Page: ' + str(self.page) + ' Offset: ' + str(self.offset)
