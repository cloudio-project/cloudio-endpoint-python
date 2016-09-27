# -*- coding: utf-8 -*-

import types
from .interface.object_container import CloudioObjectContainer
from .exception.cloudio_modification_exception import CloudioModificationException
from .topicuuid import TopicUuid
from .cloudio_object import CloudioObject


class CloudioNode(CloudioObjectContainer):
    def __init__(self):
        self.parent = None
        self.name = None
        self.interfaces = {}
        self.objects = {}           # type: {CloudioObject}

        self._updateCloudioObjects()

        # TODO Implement add to annotation
        self._addImplementedInterfaceToAnnotation()

    def _updateCloudioObjects(self):
        # Check each field of the actual node
        for field in dir(self):
            # Check if it is an attribute and ...
            attr = getattr(self, field)
            if attr:
                if isinstance(attr, CloudioObject):
                    print 'Node: Got an attribute based on an CloudioObject class'

    def _addImplementedInterfaceToAnnotation(self):
        pass

    ######################################################################
    # Interface implementations
    #
    def getUuid(self):
        # TODO Store topic uuid as attribute
        return TopicUuid(self)

    def getName(self):
        return self.name

    def setName(self, name):
        # If the node already has a name (we are renaming the node)
        # then fail with a runtime exception.
        if self.name:
            raise CloudioModificationException('The node has already a name (Renaming objects is forbidden)!')

        # Set the local name
        self.name = name

    def getObjects(self):
        return self.objects

    def getParentNodeContainer(self):
        return self.parent

    def setParentNodeContainer(self, nodeContainer):
        # If the object already has a parent (we are moving the object)
        # then fail with a runtime exception.
        if self.parent:
            raise CloudioModificationException('The parent of a Node can never be changed ' +
                                               '(Nodes can not be moved)!')

        # Set the parent
        self.parent = nodeContainer

    def getParentObjectContainer(self):
        return None

    def setParentObjectContainer(self, objectContainer):
        raise CloudioModificationException('A node can not have an object container as parent!')

    def attributeHasChangedByEndpoint(self, attribute):
        if self.parent:
            self.parent.attributeHasChangedByEndpoint(attribute)

    def attributeHasChangedByCloud(self, attribute):
        if self.parent:
            self.parent.attributeHasChangedByCloud(attribute)

    def isNodeRegisteredWithinEndpoint(self):
        return self.parent and self.parent.isNodeRegisteredWithinEndpoint()

    def findAttribute(self, location):
        """Searches for an attribute.

        :param location: List containing the 'topic levels' constructed out of the topic uuid identifying the attribute.
        :type location [str]
        :return: The cloudio object found or None
        """
        if location:
            if len(location) > 0:
                if location[-1] == u'objects':      # Compare with the last element
                    location.pop()     # Remove last item (peek item)
                    if len(location) > 0:
                        # Get object from container (dictionary) by key
                        obj = self.getObjects()[location.pop()]
                        if obj:
                            return obj.findAttribute(location)
        return None
