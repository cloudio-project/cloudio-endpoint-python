# -*- coding: utf-8 -*-

class PropertiesEndpointConfiguration():

    def __init__(self, properties):
        self._properties = properties   # type: dict

    def getProperty(self, key, defaultValue=''):
        """
        :param key: The key of interest
        :param defaultValue: Alternative value if property does not exist.
        :return: The property value
        :rtype: str
        """
        if key in self._properties:
            return self._properties[key]
        else:
            return defaultValue

    def containsKey(self, key):
        """
        :param key: The key of interest
        :type key: str
        :return: True if the property with the key exists
        :rtype: bool
        """
        return key in self._properties
