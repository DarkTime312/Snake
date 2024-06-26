from collections import deque


class LimitedList:
    """
    A class representing a list with a maximum size limit.

    This class implements a list-like data structure that maintains a maximum size.
    When the maximum size is reached, adding new items removes the oldest items.

    Attributes:
        _max_size (int): The maximum number of items the list can hold.
        items (deque): A double-ended queue to store the items.

    Methods:
        add(item): Adds an item to the list.
        __getitem__(index): Allows indexing and slicing of the list.
        __iter__(): Makes the class iterable.
    """
    def __init__(self, max_size):
        """
        Initialize the LimitedList with a maximum size.

        Args:
            max_size (int): The maximum number of items the list can hold.
        """
        self._max_size = max_size
        self.items = deque(maxlen=max_size)

    @property
    def max_size(self):
        """
        Get the maximum size of the list.

        Returns:
            int: The maximum number of items the list can hold.
        """
        return self._max_size

    @max_size.setter
    def max_size(self, new_max_size):
        """
        Set a new maximum size for the list.

        If the new size is smaller than the current number of items,
        excess items are removed from the left (oldest first).

        Args:
            new_max_size (int): The new maximum size for the list.
        """
        if new_max_size < len(self.items):
            # If new size is smaller, remove excess items from the left
            while len(self.items) > new_max_size:
                self.items.popleft()
        self._max_size = new_max_size
        self.items = deque(self.items, maxlen=new_max_size)

    def add(self, item):
        """
        Add an item to the list.

        If the list is at maximum capacity, the oldest item is removed.

        Args:
            item: The item to be added to the list.
        """
        self.items.append(item)

    def __getitem__(self, index):
        """
        Enable indexing and slicing of the list.

        Args:
            index: An integer index or a slice object.

        Returns:
            The item at the given index or a list of items for a slice.

        Raises:
            IndexError: If the index is out of range.
        """
        if isinstance(index, slice):
            # Convert the deque to a list and return the sliced portion
            return list(self.items)[index]
        else:
            # Handle integer index
            return self.items[index]

    def __iter__(self):
        """
        Make the class iterable.

        Returns:
            An iterator over the items in the list.
        """
        return iter(self.items)
