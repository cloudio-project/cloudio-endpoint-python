# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from .unique_identifiable import CloudioUniqueIdentifiable


class CloudioNodeContainer(CloudioUniqueIdentifiable):
    """Interface to be implemented by all classes that can hold cloud.iO nodes."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def attribute_has_changed_by_endpoint(self, attribute):
        """The attribute has changed

        :param attribute Attribute which has changed.
        """
        pass

    @abstractmethod
    def attribute_has_changed_by_cloud(self, attribute):
        """The attribute has changed from the cloud.

        :param attribute Attribute which has changed.
        """
        pass
