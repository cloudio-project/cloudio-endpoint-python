# -*- coding: utf-8 -*-

class PropertiesEndpointConfiguration(object):

    def __init__(self, properties):
        super(PropertiesEndpointConfiguration, self).__init__()
        self._properties = properties  # type: dict

    def get_property(self, key, default_value=''):
        """
        :param key: The key of interest
        :param default_value: Alternative value if property does not exist.
        :return: The property value
        :rtype: str
        """
        if key in self._properties:
            return self._properties[key]
        else:
            return default_value

    def contains_key(self, key):
        """
        :param key: The key of interest
        :type key: str
        :return: True if the property with the key exists
        :rtype: bool
        """
        return key in self._properties
