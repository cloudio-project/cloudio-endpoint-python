# -*- coding: utf-8 -*-

from interface.object_container import CloudioObjectContainer
from interface.attribute_container import CloudioAttributeContainer
from cloudio_attribute import CloudioAttribute

class CloudioObject():
    def __init__(self):
        self._test = 'sdasdf'
        self._internal = _InternalObject(self)

class _InternalObject(CloudioObjectContainer, CloudioAttributeContainer):

    def __init__(self, externalObject):
        self._externalObject = externalObject
        self.parent = None      # type: CloudioObjectContainer
        self.name = None        # type: str
        self.conforms = None
        self.objects = {}
        self.attributes = {}
        self.staticAttributesAdded = False

        # Check each field of the actual CloudioObject object.
        for field in dir(externalObject):
            # Check if it is an attribute and go get it
            attr = getattr(externalObject, field)
            if attr:
                if isinstance(attr, CloudioObject):
                   print 'Got an attribute based on an CloudioObject class'
                elif type(field) == CloudioAttribute:
                    print 'Got an attribute based on an CloudioAttribute class'
                else:
                    print 'Got an attribute with non-relevant type'

    def getExternalObject(self):
        return self._externalObject

    ######################################################################
    # Interface implementations
    #
    def getUuid(self):
        return super(_InternalObject, self).getUuid()

    def setName(self, name):
        super(_InternalObject, self).setName(name)

    def getName(self):
        return super(_InternalObject, self).getName()

    def attributeHasChangedByCloud(self, attribute):
        super(_InternalObject, self).attributeHasChangedByCloud(attribute)

    def isNodeRegisteredWithinEndpoint(self):
        return super(_InternalObject, self).isNodeRegisteredWithinEndpoint()

    def attributeHasChangedByEndpoint(attribute):
        super(_InternalObject, attribute).attributeHasChangedByEndpoint()

    def getObjects(self):
        return super(_InternalObject, self).getObjects()

    def setParentObjectContainer(self, objectContainer):
        super(_InternalObject, self).setParentObjectContainer(objectContainer)

    def getParentNodeContainer(self):
        super(_InternalObject, self).getParentNodeContainer()

    def getParentObjectContainer(self):
        super(_InternalObject, self).getParentObjectContainer()

    def setParentNodeContainer(self, nodeContainer):
        super(_InternalObject, self).setParentNodeContainer(nodeContainer)

    def findAttribute(self, location):
        super(_InternalObject, self).findAttribute(location)

    def getAttributes(self):
        super(_InternalObject, self).getAttributes()

    ######################################################################
    # Privte methods
    #
    def getConforms(self):
        return None

    def setConforms(self, dataClass):
        pass
