# -*- coding: utf-8 -*-


class PendingUpdate:
    def __init__(self, data):
        if isinstance(data, (bytes, bytearray)):
            # Convert bytes to string
            self.data = data.decode('utf-8')
        else:
            assert isinstance(data, str), 'Must be a string'
            self.data = data

    def get_header_bytes(self):
        """Returns the contained data."""
        return self.data

    @classmethod
    def get_uuid_from_persistence_key(cls, key):
        """Extracts the endpoint's uuid from the key used to locally store a cloud.iO message.
        """
        return key[14:key.rfind('-')].replace(';', '/')
