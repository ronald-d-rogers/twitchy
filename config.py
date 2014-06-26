"""JSON configuration codec and file handlers

Returns ASCII instead of unicode strings for compatibility
Encodes and decodes tuples
"""

import json
import collections


class ConfigurationError(Exception):
    pass


def encode(obj):
    if isinstance(obj, tuple):
        return {'__type__': 'tuple', 'items': [encode(x) for x in obj]}
    if isinstance(obj, list):
        return [encode(x) for x in obj]
    if isinstance(obj, dict):
        return dict((k, encode(v)) for k, v in obj.iteritems())
    return obj


def decode(obj):
    if isinstance(obj, dict):
        if obj.get('__type__') == 'tuple':
            return tuple(decode(obj['items']))
        else:
            return dict((decode(key), decode(value)) for key, value in obj.iteritems())
    elif isinstance(obj, list):
        return [decode(element) for element in obj]
    elif isinstance(obj, unicode):
        return obj.encode('utf-8')
    else:
        return obj


class Encoder(json.JSONEncoder):

    def encode(self, obj):
        return super(Encoder, self).encode(encode(obj))


class Decoder(json.JSONDecoder):

    def decode(self, obj):
        return decode(super(Decoder, self).decode(obj))


def write(filepath, dict_, encoder=Encoder):
    enc = encoder()

    with open(filepath, 'w') as f:
        f.write(enc.encode(dict_))


def read(filepath, decoder=Decoder):
    dec = decoder()

    with open(filepath, 'r') as f:
        return dec.decode(f.read())


class Config(collections.MutableMapping):
    def __init__(self, path, encoder=Encoder, decoder=Decoder):
        self.path = path
        self.encoder = encoder
        self.decoder = decoder

        if not path:
            raise ValueError('path not set or set to None')

        try:
            self._dict = ConfigDict(self, read(self.path, self.decoder))
        except IOError:
            self._dict = ConfigDict(self, {})

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def setdefault(self, key, value):
        return self._dict.setdefault(key, value)

    def write(self):
        write(self.path, self._dict.dict(), self.encoder)


class ConfigDict(collections.MutableMapping):

    def __init__(self, config, dict_):
        self.config = config
        self._dict = dict_

    def __getitem__(self, key):
        value = self._dict[key]

        if isinstance(value, dict):
            return ConfigDict(self.config, value)
        else:
            return value

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def setdefault(self, key, value):
        value = super(ConfigDict, self).setdefault(key, value)

        if isinstance(value, dict):
            return ConfigDict(self.config, value)
        else:
            return value

    def dict(self):
        return self._dict

    def write(self):
        self.config.write()
