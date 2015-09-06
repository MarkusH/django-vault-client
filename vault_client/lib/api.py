"""
The Django-Vault Client API.
"""
from functools import wraps
import json

import requests
from requests.exceptions import HTTPError

from .vault import Item, Key


class VaultException(Exception):
    pass


class LoginRequired(VaultException):
    pass


class APIException(VaultException):

    def __init__(self, e):
        self.__cause__ = e
        msg = ['%s:' % e.args[0]]
        content_type = e.response.headers.get('Content-Type', 'text/plain')
        if content_type == 'application/json':
            errors = e.response.json()
            for field, values in errors.items():
                msg.append('\t%(f)s: %(e)s' % {'f': field, 'e': ' '.join(values)})
        else:
            msg.append(e.response.text)
        super().__init__('\n'.join(msg))


def login_required(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.logged_in:
            name = f.__name__
            raise LoginRequired('You need to login before calling %s.' % name)
        return f(self, *args, **kwargs)
    return wrapper


class API(object):

    API_BASE_URL = '/api/v1'

    API_URLS = {
        'login': '/login/',

        'item': '/item/',
        'item-object': '/item/{uuid}/',

        'key': '/key/',
        'key-object': '/key/{uuid}/',
    }

    def __init__(self, host):
        self.host = host
        self.logged_in = False
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

    def get_credentials(self):
        """
        :returns: A dict
        """
        raise NotImplementedError("Subclasses need to implement this method")

    def login(self, **credentials):
        if not credentials:
            credentials = self.get_credentials()
        data = json.dumps(credentials)
        response = self.session.post(self.get_url('login'), data=data)
        self.logged_in = response.ok
        return self.logged_in

    def get_url(self, name, **kwargs):
        return self.host + self.API_BASE_URL + self.API_URLS[name].format(**kwargs)

    def _get(self, url, **kwargs):
        response = self.session.get(self.get_url(url, **kwargs))
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise APIException(e)
        return response.json()

    def _save(self, create_url, update_url, obj):
        data = obj.to_json()
        if obj.uuid:  # update
            response = self.session.put(self.get_url(update_url, uuid=obj.uuid), data=data)
        else:  # create new
            response = self.session.post(self.get_url(create_url), data=data)
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise APIException(e)
        return obj.refresh(response.json())

    def _delete(self, url, uuid):
        response = self.session.delete(self.get_url(url, uuid=uuid))
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise APIException(e)

    @login_required
    def get_items(self):
        data = self._get('item')
        return [Item.from_json(data) for data in data]

    @login_required
    def get_item(self, uuid):
        if isinstance(uuid, Item):
            uuid = uuid.uuid
        data = self._get('item-object', uuid=uuid)
        return Item.from_json(data)

    @login_required
    def save_item(self, item):
        return self._save('item', 'item-object', item)

    @login_required
    def delete_item(self, uuid):
        if isinstance(uuid, Item):
            uuid = uuid.uuid
        self._delete('item-object', uuid=uuid)

    @login_required
    def get_keys(self):
        data = self._get('key')
        return [Key.from_json(data) for data in data]

    @login_required
    def save_key(self, key):
        return self._save('key', 'key-object', key)

    @login_required
    def get_key(self, uuid):
        if isinstance(uuid, Key):
            uuid = uuid.uuid
        data = self._get('key-object', uuid=uuid)
        return Key.from_json(data)

    @login_required
    def delete_key(self, uuid):
        if isinstance(uuid, Key):
            uuid = uuid.uuid
        self._delete('key-object', uuid=uuid)
