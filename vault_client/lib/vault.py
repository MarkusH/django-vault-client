import base64
import json
import uuid

from dateutil.parser import parse as parse_datetime


def parse_b64(value):
    return base64.b64decode(value.encode('utf-8'), validate=True)


def parse_dt(value):
    if isinstance(value, str):
        return parse_datetime(value).replace(microsecond=0, tzinfo=None)
    return value


def parse_uuid(value):
    if isinstance(value, str):
        return uuid.UUID(value)
    return value


def serialize_b64(value):
    return base64.b64encode(value).decode('utf-8')


class Item(object):

    def __init__(self, name, value, date_added=None, date_updated=None, owner=None, uuid=None):
        self.name = name
        self.value = value

        self._date_added = parse_dt(date_added)
        self._date_updated = parse_dt(date_updated)
        self._owner = owner
        self._uuid = parse_uuid(uuid)
        self._encrypted = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Item %s "%s">' % (self.uuid, self.name)

    @property
    def date_added(self):
        return self._date_added

    @property
    def date_updated(self):
        return self._date_updated

    @property
    def owner(self):
        return self._owner

    @property
    def uuid(self):
        return self._uuid

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value.encode('utf-8') if isinstance(value, str) else value

    @classmethod
    def from_json(cls, data):
        """
        The vault item export format from the API::

            data = {
                "date_added": "2015-09-01T07:27:36.515Z",
                "date_updated": "2015-09-01T07:27:36.542Z",
                "name": "name1"
                "owner": 1,
                "uuid": "21339795-a7a0-43c9-ba69-1879a35036d7",
                "value": "hQIMAz1yevDqoj6+AQ...svEDswYTHRB8c0BQSWLP",
            }
        """
        obj = cls(
            name=data['name'],
            value=parse_b64(data['value']),
            date_added=parse_dt(data['date_added']),
            date_updated=parse_dt(data['date_updated']),
            owner=data['owner'],
            uuid=parse_uuid(data['uuid']),
        )
        obj._encrypted = True
        return obj

    def to_json(self):
        return json.dumps({
            "name": self.name,
            "value": serialize_b64(self.value),
            "encrypted": self._encrypted,
        })

    def refresh(self, data):
        """
        The vault item export format from the API::

            data = {
                "date_added": "2015-09-01T07:27:36.515Z",
                "date_updated": "2015-09-01T07:27:36.542Z",
                "name": "name1"
                "owner": 1,
                "uuid": "21339795-a7a0-43c9-ba69-1879a35036d7",
                "value": "hQIMAz1yevDqoj6+AQ...svEDswYTHRB8c0BQSWLP",
            }
        """
        self.name = data['name']
        self.value = parse_b64(data['value'])

        self._date_added = parse_dt(data['date_added'])
        self._date_updated = parse_dt(data['date_updated'])
        self._owner = data['owner']
        self._uuid = parse_uuid(data['uuid'])
        self._encrypted = True
        return self


class Key(object):

    def __init__(self, key, date_added=None, date_updated=None, fingerprint=None, owner=None, uuid=None):
        self.key = key

        self._date_added = parse_dt(date_added)
        self._date_updated = parse_dt(date_updated)
        self._fingerprint = fingerprint
        self._owner = owner
        self._uuid = parse_uuid(uuid)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Key %s "%s">' % (self.uuid, self.key)

    @property
    def date_added(self):
        return self._date_added

    @property
    def date_updated(self):
        return self._date_updated

    @property
    def fingerprint(self):
        return self._fingerprint

    @property
    def owner(self):
        return self._owner

    @property
    def uuid(self):
        return self._uuid

    @classmethod
    def from_json(cls, data):
        """
        The vault item export format from the API::

            data = {
              "date_added" : "2015-09-01T07:25:28.393Z",
              "date_updated" : "2015-09-01T07:25:36.720Z"
              "fingerprint" : "5786 D19B C800 5CE5 7452  0A63 AFE7 9D68 D41C 7E39",
              "key" : "5786D19BC8005CE574520A63AFE79D68D41C7E39",
              "owner" : 1,
              "uuid" : "185d8da9-899b-4e92-9167-bffe9b786ac2",
           }
        """
        return cls(
            date_added=parse_dt(data['date_added']),
            date_updated=parse_dt(data['date_updated']),
            fingerprint=data['fingerprint'],
            key=data['key'],
            owner=data['owner'],
            uuid=parse_uuid(data['uuid']),
        )

    def to_json(self):
        return json.dumps({
            "key": self.key,
        })

    def refresh(self, data):
        """
        The vault item export format from the API::

            data = {
              "date_added" : "2015-09-01T07:25:28.393Z",
              "date_updated" : "2015-09-01T07:25:36.720Z"
              "fingerprint" : "5786 D19B C800 5CE5 7452  0A63 AFE7 9D68 D41C 7E39",
              "key" : "5786D19BC8005CE574520A63AFE79D68D41C7E39",
              "owner" : 1,
              "uuid" : "185d8da9-899b-4e92-9167-bffe9b786ac2",
           }
        """
        self.key = data['key']

        self._date_added = parse_dt(data['date_added'])
        self._date_updated = parse_dt(data['date_updated'])
        self._fingerprint = data['fingerprint']
        self._owner = data['owner']
        self._uuid = parse_uuid(data['uuid'])
        return self
