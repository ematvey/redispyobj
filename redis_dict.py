import re

from redis_list import RedisList
from redis_set import RedisSet


class RedisDict(object):  # move to ABC mapping

    _repr_sep = '.'  # separator to use when repr-ing
    _allowed_key_chars = 'a-zA-Z0-9_'
    _re_path_template = (r'^{root}{sep}(?P<key>[{key_chars}]+)'
                         r'({sep}(?P<tail>[{key_chars}{sep}]+))?')
    _dict_marker = '[dictroot]'
    _keyset_field = '[keys]'

    def __init__(self, redis, root_key, separator='.'):
        if separator in self._allowed_key_chars:
            raise ValueError("Separator can't be among allowed key chars")
        self.r = redis
        self.root_key = root_key
        self.sep = separator
        self._path = self.root_key + self.sep
        self._keyset_key = self._path + self._keyset_field
        self._marker_key = self._path + self._dict_marker

        if self.r.get(self.root_key) == self._dict_marker:
            keyset_type = self.r.type(self._keyset_key)
            if keyset_type == 'none':
                raise RedisDictInitializationError('Dict marker present but '
                                                   'no keyset')
            elif keyset_type != 'set':
                raise RedisDictTypeError('Keyset field is of wrong type')
        else:
            self.r.set(self._marker_key, self._dict_marker)

        self._re_path = self._re_path_template.format(
            root=self.root_key,
            sep=self.sep,
            key_chars=self._allowed_key_chars)
        self.re_keys = re.compile(self._re_path)

    def __repr__(self):
        return "%s('%s', keys: %s)" % (
            self.__class__.__name__,
            self.root_key.replace(self.sep, self._repr_sep) if
                self._repr_sep != self.sep else self.root_key,
            list(self.keys()),
        )

    def keys(self):
        return self.r.smembers(self._keyset_key)  # TODO replace with RedisSet

    def values(self):
        raise NotImplementedError('Not supported')

    def _check_key_validity(self, key):
        if not (isinstance(key, str) or isinstance(key, unicode)):
            raise RedisDictTypeError('key is expected to be string')

    def __getitem__(self, key):
        self._check_key_validity(key)
        if not key in self.keys():
            raise RedisDictKeyError
        path = self._path + key
        if self.r.exists(path + self.sep + self._dict_marker):
            return RedisDict(self.r, path, self.sep)
        if self.r.type(path) == 'list':
            return RedisList(self.r, path)
        if self.r.type(path) == 'set':
            return RedisSet(self.r, path)
        return self.r.get(path)

    def __setitem__(self, key, value):
        self._check_key_validity(key)
        path = self._path + key
        self.r.sadd(self._keyset_key, key)
        if isinstance(value, dict):
            m = RedisDict(self.r, path, self.sep)
            for k, v in value.iteritems():
                m[k] = v
        elif isinstance(value, list) or isinstance(value, tuple):
            RedisList(self.r, path).extend(value)
        elif isinstance(value, set):
            RedisSet(self.r, path).update(value)
        else:
            self.r.set(path, value)

    def __delitem__(self, key):
        self._check_key_validity(key)
        for k in self.r.keys():
            match = self.re_keys.match(k)
            if match and key == match.groupdict()['key']:
                self.r.delete(k)
        self.r.srem(self._keyset_key, key)

    def __contains__(self, key):
        return self.r.sismember(self.root_key, key)

    def __len__(self):
        return self.r.scard(self.root_key)

    def __iter__(self):
        return (k for k in self.keys())


class RedisDictInitializationError(Exception):
    pass


class RedisDictTypeError(TypeError):
    pass


class RedisDictKeyError(KeyError):
    pass
