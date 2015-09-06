import json

from os import makedirs
from os.path import dirname, exists


class Config(object):

    _keys = (
        'homedir', 'hostname', 'password', 'username',
    )

    @classmethod
    def load(cls, filename):
        makedirs(dirname(filename), exist_ok=True)
        if exists(filename):
            with open(filename, 'r') as fp:
                data = json.load(fp)
        else:
            data = {}
        config = cls()
        config._filename = filename
        for k in Config._keys:
            setattr(config, k, data.get(k, None))
        return config

    def save(self, filename=None):
        if filename is None:
            filename = self._filename
        data = {k: getattr(self, k) for k in Config._keys}
        makedirs(dirname(filename), exist_ok=True)
        with open(filename, 'w') as fp:
            json.dump(data, fp)
