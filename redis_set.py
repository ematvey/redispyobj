
class RedisSet(object):
    def __init__(self, redis, key):
        if redis.exists(key):
            if redis.type(key) != 'set':
                redis.delete(key)
        self.r = redis
        self.key = key

    def add(self, value):
        self.r.sadd(self.key, value)

    def update(self, update):
        self.r.sadd(self.key, *update)

    def remove(self, value):
        self.r.srem(self.key, value)

    def __repr__(self):
        return "RedisSet('%s', card: %s)" % (self.key, len(self))

    def __iter__(self):
        return (v for v in self.r.smembers(self.key))

    def __len__(self):
        return self.r.scard(self.key)

    def __contains__(self, value):
        return self.r.sismember(self.key, value)
