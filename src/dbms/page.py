import time

class Page:
    def __init__(self, id, data):
        self.changed = False
        self.id = id
        self.data = data
        self.time = time.time()
