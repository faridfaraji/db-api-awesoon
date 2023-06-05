from cookiecutter.core.model.storage import Storage
import uuid


class Memory(Storage):
    def __init__(self):
        self.stuffs = {}
        self.count = 0

    def store_stuff(self, stuff):
        id = uuid.uuid4()
        # store the object in memory
        self.stuffs[str(id)] = stuff
        self.count = self.count + 1

    def get_stuff(self):
        # stuff variable is MyObject type
        return [stuff.name for stuff in self.stuffs.values()]
