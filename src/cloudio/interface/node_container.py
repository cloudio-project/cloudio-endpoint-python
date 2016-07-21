# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from unique_identifiable import UniqueIdentifiable

class CloudioNodeContainer(UniqueIdentifiable):
    """Interface to be implemented by all classes that can hold cloud.iO nodes."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def attributeHasChangedByEndpoint(self, attribute):
        """The attribute has changed

        :param attribute Attribute which has changed.
        """
        pass

    @abstractmethod
    def attributeHasChangedByCloud(self, attribute):
        """The attribute has changed from the cloud.

        :param attribute Attribute which has changed.
        """
        pass
