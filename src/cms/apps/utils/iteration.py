"""Some useful iteration tools."""


from itertools import chain, islice


class CachedIterator(object):
    
    """Wraps an iterator, providing random access through the use of a cache."""
    
    __slots__ = ("_iterator", "_cache",)
    
    def __init__(self, iterator):
        """Initializes the cached iterator."""
        self._iterator = iterator
        self._cache = []
        
    def _iter_remaining(self):
        """
        Iterates over all remaining elements in the iterator, caching as it
        goes.
        """
        if self._iterator is not None:
            for item in self._iterator:
                self._cache.append(item)
                yield item
        self._iterator = None
        
    def __iter__(self):
        """Iterates over all items."""
        return chain(self._cache, self._iter_remaining())
            
    def __len__(self):
        """Returns the number of items in the iterator."""
        return len(list(iter(self)))
        
    def __getitem__(self, index):
        """Returns the item at the given inde."""
        if isinstance(index, int):
            try:
                return islice(iter(self), index, index + 1).next()
            except StopIteration:
                raise IndexError, index
        elif isinstance(index, slice):
            return list(islice(iter(self), index.start, index.stop, index.step))
        else:
            raise ValueError, "Only integer and slice indices are supported."
        
          
cache = CachedIterator

