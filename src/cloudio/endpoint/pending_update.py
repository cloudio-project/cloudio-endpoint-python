# -*- coding: utf-8 -*-


class PendingUpdate:
    def __init__(self, data):
        if isinstance(data, (bytes, bytearray)):
            # Convert bytes to string
            self._data = data.decode('utf-8')
        else:
            assert isinstance(data, str), 'Must be a string'
            self._data = data

    def get_data(self):
        """Returns the contained data."""
        return self._data

    @classmethod
    def get_uuid_from_persistence_key(cls, key):
        """Extracts the endpoint's uuid from the key used to locally store a cloud.iO message.
        """
        return key[14:key.rfind('-')].replace(';', '/')
