class RedisList(object):
    def __init__(self, redis, key):
        if redis.exists(key):

            raise Exception
        self.r = redis
        self.key = key

    def append(self, value):
        self.__iadd__(value)

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

    def __iadd__(self, value):
        self.r.lpush(self.key, value)
