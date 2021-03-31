# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from .named_item import CloudioNamedItem


class CloudioUniqueIdentifiable(CloudioNamedItem):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_uuid(self):
        """Returns a unique ID object that identifies the CloudioUniqueIdentifiable object.

        :return: The UUID object of the CloudioUniqueIdentifiable object.
        :rtype: interface.uuid.CloudioUuid
        """
        pass
