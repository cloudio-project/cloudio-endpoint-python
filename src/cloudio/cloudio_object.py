# -*- coding: utf-8 -*-

import types
from .interface.object_container import CloudioObjectContainer
from .interface.attribute_container import CloudioAttributeContainer
from .exception.invalid_cloudio_attribute_exception import InvalidCloudioAttributeException
from .exception.cloudio_modification_exception import CloudioModificationException
from .cloudio_attribute import CloudioAttribute
from .topicuuid import TopicUuid

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
        # TODO Store topic uuid as attribute
        return TopicUuid(self)

    def setName(self, name):
        # If the object already has a name (we are renaming the object)
        # then fail with a runtime exception.
        if self.name:
            raise CloudioModificationException('The Object has already a name (Renaming objects is forbidden)!')

        # Set the local name
        self.name = name

    def getName(self):
        return self.name

    def attributeHasChangedByCloud(self, attribute):
        if self.parent:
            self.parent.attributeHasChangedByCloud(attribute)

    def isNodeRegisteredWithinEndpoint(self):
        return self.parent and self.parent.isNodeRegisteredWithinEndpoint()

    def attributeHasChangedByEndpoint(self, attribute):
        if self.parent:
            self.parent.attributeHasChangedByEndpoint(attribute)

    def getObjects(self):
        return self.objects

    def setParentObjectContainer(self, objectContainer):
        # If the object already has a parent (we are moving the object)
        # then fail with a runtime exception.
        if self.parent:
            raise CloudioModificationException('The parent of an Object can never be changed ' +
                                               '(Objects can not be moved)!')

        # Set the parent
        self.parent = objectContainer

    def getParentNodeContainer(self):
        return None

    def getParentObjectContainer(self):
        return self.parent

    def setParentNodeContainer(self, nodeContainer):
        raise CloudioModificationException(u'As this is not a node, it can not be embedded into a node container!')

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
                        object = self.getObjects().getItem(location.pop(0))
                        if object:
                            return object.findAttribute(location)
                elif location[0] == u'attributes':
                    self.getAttributes()    # Update attributes list
                    location.pop(0)         # Remove first item
                    if len(location) > 0:
                        attribute = self.getAttributes().getItem(location.pop(0))
                        if attribute:
                            return attribute
        return None

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
