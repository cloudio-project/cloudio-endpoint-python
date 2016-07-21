# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from unique_identifiable import UniqueIdentifiable

class CloudioObjectContainer(UniqueIdentifiable):
    """Interface to be implemented by all classes that can hold cloud.iO objects."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def attributeHasChangedByEndpoint(attribute):
        """
        :param attribute: Attribute which has changed.
        :type attribute: CloudioAttribute
        """
        pass

    @abstractmethod
    def attributeHasChangedByCloud(self, attribute):
        """The attribute has changed from the cloud.
        :param attribute Attribute which has changed.
        :type attribute CloudioAttribute
        """
        pass

    @abstractmethod
    def isNodeRegisteredWithinEndpoint(self):
        """Returns true if the node the attribute is part of is registered within an endpoint, false otherwise.
        :return True if the node is registered within the endpoint, false if not.
        :rtype: bool
        """
        pass

    @abstractmethod
    def getObjects(self):
        """Returns the list of child object contained inside this container.
        :return Child objects
        :rtype: {CloudioObject}
        """
        pass

    @abstractmethod
    def getParentObjectContainer(self):
        """Returns the object container's parent object container. Note that if the actual object container is not embedded
           into another object controller, the method returns null.
        """
        pass

    @abstractmethod
    def setParentObjectContainer(self, objectContainer):
        """Sets the parent object container of the object container. Note that object containers can not be moved, so
           this method throws a runtime exception if someone tries to move the object container to a new parent or in the
           case the actual container is a node, which can not be part of another object container.
        """
        pass

    @abstractmethod
    def getParentNodeContainer(self):
        """Returns the object container's parent node container. Note that if the actual object container is not a node,
           the method returns null.
        """
        pass

    @abstractmethod
    def setParentNodeContainer(self, nodeContainer):
        """Sets the parent node container of the object container (node). Note that object containers can not be moved, so
           this method throws a runtime exception if someone tries to move the object container to a new parent or in the
           case the actual container is not a node.
        """
        pass

    @abstractmethod
    def findAttribute(self, location):
        """Finds the given attribute inside the child objects using the given location path (stack). If an attribute was
           found at the given location, a reference to that attribute is returned, otherwise null is returned.
        """
        pass