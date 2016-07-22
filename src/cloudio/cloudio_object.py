# -*- coding: utf-8 -*-

import types
from .interface.object_container import CloudioObjectContainer
from .interface.attribute_container import CloudioAttributeContainer
from .cloudio_attribute import CloudioAttribute
from .exception.invalid_cloudio_attribute_exception import InvalidCloudioAttributeException
from .exception.cloudio_modification_exception import CloudioModificationException

class CloudioObject():
    def __init__(self):
        self._internal = _InternalObject(self)

class _InternalObject(CloudioObjectContainer, CloudioAttributeContainer):

    def __init__(self, externalObject):
        self._externalObject = externalObject
        self.parent = None      # type: CloudioObjectContainer
        self.name = None        # type: str
        self.conforms = None
        self.objects = {}
        self._attributes = {}
        self._staticAttributesAdded = False

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
        """Returns the contained attributes in this object as a list
        :return A dictionary of attributes
        :rtype {CloudioAttribute}
        """
        # If it is the first call, get all attributes of the CloudioObject
        # and put it into the 'attributes' attribute
        if not self._staticAttributesAdded:
            # Check each field of the actual CloudioObject object.
            for field in dir(self._externalObject):
                # Check if it is an attribute and go get it
                attr = getattr(self._externalObject, field)
                if attr:
                    # Check if it is a static value (means an attribute
                    # with a standard type)
                    #
                    # Check if it is a bool, int, float, string
                    if isinstance(attr, bool)  or \
                       isinstance(attr, int)   or \
                       isinstance(attr, float) or \
                       isinstance(attr, str):
                        attribute = CloudioAttribute()
                        attribute._internal.setConstraint('static')
                        attribute._internal.setName(field)
                        attribute._internal.setParent(self)
                        attribute._internal.setStaticValue(attr)

                        topicUuid = attribute._internal.getUuid().toString()
                        if topicUuid and not topicUuid in self._attributes:
                            self._attributes[topicUuid] = attribute
                        else:
                            raise CloudioModificationException('Duplicate name for fields')

                    elif isinstance(attr, types.MethodType) or \
                         isinstance(attr, types.InstanceType) or \
                         isinstance(attr, _InternalObject):
                        pass
                    else:
                        raise InvalidCloudioAttributeException(type(attr))

            self._staticAttributesAdded = True

        return self._attributes

    ######################################################################
    # Privte methods
    #
    def _getConforms(self):
        return None

    def _setConforms(self, dataClass):
        pass
