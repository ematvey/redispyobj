class RedisList(object):
    def __init__(self, redis, key):
        if redis.exists(key):
            if redis.type(key) != 'list':
                redis.delete(key)
        self.r = redis
        self.key = key

    def append(self, value):
        self.r.rpush(self.key, value)

    def extend(self, values):
        self.r.rpush(self.key, *values)

    def remove(self, value, count=0):
        self.r.lrem(self.key, value, 0)

    def __repr__(self):
        return "RedisList('%s', length: %s)" % (self.key, len(self))

    def __getitem__(self, indexer):
        if isinstance(indexer, slice):
            if not indexer.step is None:
                raise NotImplementedError
            start = indexer.start
            stop = indexer.stop
            if stop < 0:
                stop = len(self) + stop
            return self.r.lrange(self.key, start, stop)
        return self.r.lindex(self.key, indexer)

    def __setitem__(self, index, value):
        if not isinstance(index, int):
            raise Exception
        self.r.lset(self.key, index, value)

    def __iter__(self):
        return (self.r.lindex(self.key, i) for i in xrange(len(self)))

    def __iadd__(self, values):
        self.extend(values)
        return self

    def __len__(self):
        return self.r.llen(self.key)

    def __contains__(self, value):
        raise NotImplementedError
