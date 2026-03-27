import threading

class Vector:
    def __init__(self, data=None):
        if data is None:
            data = []
        self.data = data
        self.dirty = True
        self.lock = threading.Lock()
    def __getitem__(self, index):
        return self.data[index]
    def __setitem__(self, index, value):
        with self.lock:
            self.data[index] = value
            self.dirty = True
    def read(self):
        d = None
        with self.lock:
            d = self.data.copy()
            self.dirty = False
        return d

class VectorBuffer:
    def __init__(self, vecs:dict[str,list[float]]):
        # vecs = {'V': [,,,,,], 'U': [,,,,,], 'P': [,,,,,], 'O': [,,]}
        self.vecs = {
            k: Vector(v)
            for k, v in vecs.items()
        }
    def __getitem__(self, key):
        return self.vecs[key]
    def read(self):
        return {k: v.read() for k, v in self.vecs.items()}
    def get_updates(self):
        return {k: v.read() for k, v in self.vecs.items() if v.dirty}
    @property
    def dirty(self):
        return any([v.dirty for v in self.vecs.values()])




