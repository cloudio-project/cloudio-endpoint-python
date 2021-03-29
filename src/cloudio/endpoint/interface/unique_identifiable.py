# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from .named_item import NamedItem


class UniqueIdentifiable(NamedItem):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_uuid(self):
        """Returns a unique ID object that identifies the UniqueIdentifiable object.

        :return: The UUID object of the UniqueIdentifiable object.
        :rtype: interface.uuid.Uuid
        """
        pass
