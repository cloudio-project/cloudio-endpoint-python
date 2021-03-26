# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from .unique_identifiable import UniqueIdentifiable


class CloudioAttributeContainer(UniqueIdentifiable):
    """Interface to be implemented by all classes that can hold attributes."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def attribute_has_changed_by_endpoint(self, attribute):
        """The attribute has changed local in the application.

        :param attribute Attribute which has changed.
        """
        pass

    @abstractmethod
    def attribute_has_changed_by_cloud(self, attribute):
        """The attribute has changed from the cloud.

        :param attribute Attribute which has changed.
        """
        pass

    @abstractmethod
    def is_node_registered_within_endpoint(self):
        """Returns true if the node the attribute is part of is registered within an endpoint, false otherwise.

        :return True if the node is registered within the endpoint, false if not.
        """
        pass

    @abstractmethod
    def get_attributes(self):
        """Returns the list of attributes contained inside this object.

        :return List of attributes.
        """
        pass

    @abstractmethod
    def get_parent_object_container(self):
        """Returns the attribute container's parent (has to be an CloudioObjectContainer).

        :return AttributeContainer's parent.
        """
        pass

    @abstractmethod
    def set_parent_object_container(self, object_container):
        """Sets the parent object container of the attribute container. Note that
           attribute containers can not be moved, so this method throws a runtime exception
           if someone tries to move the attribute container to a new parent.

        :param object_container The new parent object container.
        """
        pass
