# -*- coding: utf-8 -*-

from .interface.object_container import CloudioObjectContainer
from .exception.cloudio_modification_exception import CloudioModificationException
from .topicuuid import TopicUuid


class CloudioNode(CloudioObjectContainer):
    def __init__(self):
        self.parent = None
        self.name = None
        self.interfaces = {}
        self.objects = {}

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
        return None

    def setParentNodeContainer(self, nodeContainer):
        # If the object already has a parent (we are moving the object)
        # then fail with a runtime exception.
        if self.parent:
            raise CloudioModificationException('The parent of a Node can never be changed ' +
                                               '(Nodes can not be moved)!')

        # Set the parent
        self.parent = nodeContainer

    def getParentObjectContainer(self):
        return self.parent

    def setParentObjectContainer(self, objectContainer):
        # If the node already has a parent (we are moving the node)
        # then fail with a runtime exception.
        if self.parent:
            raise CloudioModificationException('The parent of an node can never be changed ' +
                                               '(Nodes can not be moved)!')

        # Set the parent
        self.parent = objectContainer

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
                if location[0] == u'objects':
                    location.pop(0)     # Remove first item
                    if len(location) > 0:
                        obj = self.getObjects().getItem(location.pop(0))
                        if obj:
                            return obj.findAttribute(location)
        return None
