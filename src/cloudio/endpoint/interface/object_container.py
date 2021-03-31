# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from .unique_identifiable import CloudioUniqueIdentifiable


class CloudioObjectContainer(CloudioUniqueIdentifiable):
    """Interface to be implemented by all classes that can hold cloud.iO objects."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def attribute_has_changed_by_endpoint(self, attribute):
        """
        :param attribute: Attribute which has changed.
        :type attribute: CloudioAttribute
        """
        pass

    @abstractmethod
    def attribute_has_changed_by_cloud(self, attribute):
        """The attribute has changed from the cloud.
        :param attribute Attribute which has changed.
        :type attribute CloudioAttribute
        """
        pass

    @abstractmethod
    def is_node_registered_within_endpoint(self):
        """Returns true if the node the attribute is part of is registered within an endpoint, false otherwise.
        :return True if the node is registered within the endpoint, false if not.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_objects(self):
        """Returns the list of child object contained inside this container.
        :return Child objects
        :rtype: {CloudioObject}
        """
        pass

    @abstractmethod
    def get_parent_object_container(self):
        """Returns the object container's parent object container. Note that if the actual
        object container is not embedded into another object controller, the method returns null.
        """
        pass

    @abstractmethod
    def set_parent_object_container(self, object_container):
        """Sets the parent object container of the object container. Note that object containers
        can not be moved, so this method throws a runtime exception if someone tries to move the
        object container to a new parent or in the case the actual container is a node, which can
        not be part of another object container.
        """
        pass

    @abstractmethod
    def get_parent_node_container(self):
        """Returns the object container's parent node container. Note that if the actual object
        container is not a node, the method returns null.
        """
        pass

    @abstractmethod
    def set_parent_node_container(self, node_container):
        """Sets the parent node container of the object container (node). Note that object
        containers can not be moved, so this method throws a runtime exception if someone tries
        to move the object container to a new parent or in the case the actual container is not
        a node.
        """
        pass

    @abstractmethod
    def find_attribute(self, location):
        """Finds the given attribute inside the child objects using the given location
        path (stack). If an attribute was found at the given location, a reference to that
        attribute is returned, otherwise null is returned.
        """
        pass

    @abstractmethod
    def find_object(self, location):
        """Finds the given object inside the objects tree using the given location
        path (stack). If the object was found at the given location, a reference to
        that object is returned, otherwise null is returned.
        """
        pass
