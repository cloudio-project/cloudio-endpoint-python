# -*- coding: utf-8 -*-

import utils.py_version_compatibility as types
from .interface.object_container import CloudioObjectContainer
from .interface.attribute_container import CloudioAttributeContainer
from .exception.invalid_cloudio_attribute_exception import InvalidCloudioAttributeException
from .exception.cloudio_modification_exception import CloudioModificationException
from .cloudio_attribute import CloudioAttribute
from .topicuuid import TopicUuid


class CloudioObject():
    """Base class for all cloud.iO objects.

    An object can either contain attributes (CloudioAttribute, @StaticAttribute) or child
    objects. Using this it is possible to create data models with a great flexibility.

    An object can be annotated with the @Conforms annotation to conform to a cloud.io class. A class in cloud.io is just
    a scheme what attributes and child objects an object has to have. An object is conform to such a scheme if it
    matches exactly the structure of the class. It can not contain more attributes or child objects, then it would be
    not anymore conform to that class.

    Todo: Add example code.

    """
    def __init__(self):
        self._internal = _InternalObject(self)

    def getName(self):
        return self._internal.getName()

    def setName(self, name):
        self._internal.setName(name)

    def findAttribute(self, location):
        return self._internal.findAttribute(location)

    def findObject(self, location):
        return self._internal.findObject(location)

    def getAttributes(self):
        return self._internal.getAttributes()

    def attributeHasChangedByEndpoint(self, attribute):
        self._internal.attributeHasChangedByEndpoint(attribute)

    def attributeHasChangedByCloud(self, attribute):
        self._internal.attributeHasChangedByCloud(attribute)

    def isNodeRegisteredWithinEndpoint(self):
        return self._internal.isNodeRegisteredWithinEndpoint()

    def getParentObjectContainer(self):
        return self._internal.getParentObjectContainer()

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
#           if attr:
#               if isinstance(attr, CloudioObject):
#                  print('Got an attribute based on an CloudioObject class')
#               elif type(field) == CloudioAttribute:
#                   print('Got an attribute based on an CloudioAttribute class')
#               else:
#                   print('Got an attribute with non-relevant type')

    def getExternalObject(self):
        return self._externalObject

    ######################################################################
    # Interface implementations
    #
    def getUuid(self):
        # TODO Store topic uuid as attribute
        return TopicUuid(self)

    def getName(self):
        return self.name

    def setName(self, name):
        # If the object already has a name (we are renaming the object)
        # then fail with a runtime exception.
        if self.name:
            raise CloudioModificationException('The Object has already a name (Renaming objects is forbidden)!')

        # Set the local name
        self.name = name

    def attributeHasChangedByEndpoint(self, attribute):
        if self.parent:
            self.parent.attributeHasChangedByEndpoint(attribute)

    def attributeHasChangedByCloud(self, attribute):
        if self.parent:
            self.parent.attributeHasChangedByCloud(attribute)

    def attributeHasChangedByCloud(self, attribute):
        if self.parent:
            self.parent.attributeHasChangedByCloud(attribute)

    def isNodeRegisteredWithinEndpoint(self):
        return self.parent and self.parent.isNodeRegisteredWithinEndpoint()

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
                if location[-1] == u'objects':  # Compare with last element (peek element)
                    location.pop()     # Remove last item
                    if len(location) > 0:
                        object = self.getObjects()[location.pop()]
                        if object:
                            return object.findAttribute(location)
                elif location[-1] == u'attributes':
                    self.getAttributes()    # Update attributes list
                    location.pop()         # Remove last item
                    if len(location) > 0:
                        if location[-1] in self.getAttributes():
                            attribute = self.getAttributes()[location.pop()]
                            if attribute:
                                return attribute
        return None

    def findObject(self, location):
        """Searches for an object.

        :param location: List containing the 'topic levels' constructed out of the topic uuid identifying the object.
        :type location [str]
        :return: The cloudio object found or None
        """
        if location:
            if len(location) > 0:
                if location[-1] == u'objects':  # Compare with last element (peek element)
                    location.pop()     # Remove last item
                    if len(location) > 0:
                        object = self.getObjects()[location.pop()]
                        return object
                elif location[-1] == u'attributes':
                    object = self.getAttributes()    # Update attributes list
                    location.pop()         # Remove last item
                    return object
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
                    if isinstance(attr, types.BooleanType)  or \
                       isinstance(attr, types.IntType)   or \
                       isinstance(attr, types.FloatType) or \
                       isinstance(attr, types.StringType) or \
                       isinstance(attr, types.UnicodeType):

                        if field not in ('__module__', '__doc__'):  # Some excludes:
                            attribute = CloudioAttribute()
                            attribute.setConstraint('static')
                            attribute.setName(field)
                            attribute.setParent(self)
                            attribute.setStaticValue(attr)

                            topicUuid = attribute.getUuid().toString()
                            if topicUuid and not topicUuid in self._attributes:
                                self._attributes[topicUuid] = attribute
                            else:
                                raise CloudioModificationException('Duplicate name for fields')

                    elif isinstance(attr, types.MethodType) or \
                         type(attr) or \
                         isinstance(attr, _InternalObject):
                        pass
                    else:
                        raise InvalidCloudioAttributeException(type(attr))

            self._staticAttributesAdded = True

        return self._attributes

    def to_json(self, encoder):
        """Pick out the attributes we want to store / publish.
        """
        attrDict = {}

        if self.conforms != None and len(self.conforms) > 0:
            attrDict['conforms'] = self.conforms

        if hasattr(self, 'objects') and len(self.objects) > 0:
            attrDict['objects'] = self.objects

        if hasattr(self, '_attributes')  and len(self._attributes) > 0:
            attrDict['attributes'] = self._attributes

        return encoder.default(attrDict)

    ######################################################################
    # Privte methods
    #
    def _getConforms(self):
        return None

    def _setConforms(self, dataClass):
        pass
