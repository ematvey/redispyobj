class RedisList(object):
    def __init__(self, redis, key):
        if redis.exists(key):
            if redis.type(key) != 'list':
                raise Exception
        self.r = redis
        self.key = key

    def append(self, value):
        self.r.rpush(self.key, value)

    def extend(self, values):
        self.r.rpush(self.key, *values)

    def __getitem__(self, indexer):
        if isinstance(indexer, slice):
            if indexer.step is None:
                raise Exception
            return self.r.lrange(self.key, indexer.start, indexer.stop)
        return self.r.lindex(self.key, indexer)

    def __setitem__(self, index, value):
        if not isinstance(index, int):
            raise Exception
        self.r.lset(self.key, index, value)

    def __delitem__(self, index):
        if not isinstance(index, int):
            raise Exception
        self.r.lrem(self.key, index)

    def __iadd__(self, values):
        self.extend(values)

    def __len__(self):
        return self.r.llen(self.key)

    def __contains__(self, value):
        raise NotImplemented('RedisList does not support this')
