# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class CloudioNamedItem(object):
    """An object owning a name.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_name(self):
        """Returns the name of the item.

        :return: Name of item
        :rtype: str
        """
        pass

    @abstractmethod
    def set_name(self, name):
        """
        Sets the local name of the item. Note that items can not be renamed, so this method should throw a runtime
        exception if someone tries to rename the item.

        :param name: The name to identify the item locally.
        :type name: str
        """
        pass
