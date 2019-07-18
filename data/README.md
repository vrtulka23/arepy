# Data manipulation routines

## cache.py

This routine is used for caching of the analized data.
It can be used to store any valid python data or data returned by a function.
```python
>>> dataOutput = (0.3,'foo',3)
>>> dataCache = cache( dataOutput, 'cacheName')
>>> print(dataCache)
(0.3,'foo',3)

>>> def fnOutput(seed):
>>>     return [i*seed for i in range(5)]
>>> dataCache = cache( fnOutput, 'cacheName', args=[3])
>>> print(dataCache)
[0,3,6,9,12]
```

One can even update recently cached data
```python
>>> def fnOutput(dataCache,seed):
>>>     if dataCache:
>>>         return dataCache+[i*seed for i in range(5)]
>>>     else:
>>>         return [i*seed for i in range(5)]
>>> for i in [3,4,5]:
>>>     dataCache = cache( fnOutput, 'cacheName', args=[i], update=True)
>>> print(dataCache)
[0,3,6,9,12,0,4,8,12,16,0,5,10,15,20]
```
