from collections import deque


class LimitedList:
    def __init__(self, max_size):
        self._max_size = max_size
        self.items = deque(maxlen=max_size)

    @property
    def max_size(self):
        return self._max_size

    @max_size.setter
    def max_size(self, new_max_size):
        if new_max_size < len(self.items):
            # If new size is smaller, remove excess items from the left
            while len(self.items) > new_max_size:
                self.items.popleft()
        self._max_size = new_max_size
        self.items = deque(self.items, maxlen=new_max_size)

    def add(self, item):
        self.items.append(item)

    def __getitem__(self, index):
        return self.items[index]

    def __iter__(self):
        return iter(self.items)
