import re


class RedisDict(object):  # move to ABC mapping

    _repr_sep = '.'
    _allowed_key_chars = 'a-zA-Z0-9_'
    _re_path_template = (r'^{root}{sep}(?P<key>[{key_chars}]+)({sep}(?P<tail>[{key_chars}{sep}]+))?')

    def __init__(self, redis, root_key, separator=':'):
        self.r = redis
        self.root_key = root_key
        # exit/setup
        self.sep = separator
        self._path = self.root_key + self.sep
        self._key_of_keyset = self._path + '<keys>'
        # self._plen = len(self._path)
        self._re_path = self._re_path_template.format(
            root=self.root_key,
            sep=self.sep,
            key_chars=self._allowed_key_chars)
        self.re_keys = re.compile(self._re_path)
        self.recreate_keys()

    def __repr__(self):
        return "%s('%s', keys=%s)" % (
            self.__class__.__name__,
            self.root_key.replace(self.sep, self._repr_sep) if
                self._repr_sep != self.sep else self.root_key,
            list(self.keys()),
        )

    def keys(self):
        return self.r.smembers(self._key_of_keyset)

    def recreate_keys(self):
        keys = []
        for k in self.r.keys(self._path + '*'):  # replace with field/SET caching
            m = self.re_keys.match(k)
            if not m is None:
                keys.append(m.groupdict()['key'])
        self.r.sadd(self._key_of_keyset, *keys)

    def _check_key_validity(self, key):
        if not (isinstance(key, str) or isinstance(key, unicode)):
            raise RedisDictTypeError('key is expected to be string')

    def __getitem__(self, key):
        # TODO list, set
        self._check_key_validity(key)
        path = self._path + key
        ks = self.r.keys(path + '*')
        if len(ks) == 1:
            return self.r.get(path)
        elif len(ks) == 0:
            raise RedisDictKeyError
        else:
            return RedisDict(self.r, path, self.sep)

    def __setitem__(self, key, value):
        self._check_key_validity(key)
        path = self._path + key
        # TODO list, set
        if isinstance(value, dict):
            m = RedisDict(self.r, path, self.sep)
            for k, v in value.iteritems():
                m[k] = v
        self.r.set(path, value)
        self.r.sadd(self._key_of_keyset, key)

    def __delitem__(self, key):
        for k in self.r.keys():
            match = self.re_keys.match(k)
            if match and key == match.groupdict()['key']:
                self.r.delete(k)
        self.r.srem(self._key_of_keyset, key)

    def __contains__(self, key):
        pass


class RedisDictTypeError(TypeError):
    pass


class RedisDictKeyError(KeyError):
    pass
