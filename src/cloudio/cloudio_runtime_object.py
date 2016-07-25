# -*- coding: utf-8 -*-

from exception.cloudio_modification_exception import CloudioModificationException
from cloudio_object import CloudioObject
from cloudio_attribute import CloudioAttribute

class CloudioRuntimeObject(CloudioObject):
    def __init__(self):
        CloudioObject.__init__(self)
        pass

    def getObject(self, name):
        """Returns the object with the given name or null if no object with the given name is part of the object.
        """
        return self._internal.objects[name]

    def addObject(self, name, clsOrObject):
        """Adds an object (or an object of the given class) with the given name to the runtime object."""
        if self._internal.isNodeRegisteredWithinEndpoint():
            raise CloudioModificationException(u'A CloudioRuntimeObject\'s structure can only be modified before' +
                                               u' it is registered within the endpoint!')

        # Check if parameter is a class
        if not isinstance(clsOrObject, CloudioObject):
            # Create an object of that class
            cls = clsOrObject
            obj = cls()  # Create an object of that class
            self.addObject(name, obj)
            return obj
        else:
            # We have an CloudioObject to add to the node
            object = clsOrObject
            object._internal.setParentObjectContainer(self)
            object._internal.setName(name)

            # Add object to the objects container
            assert not self._internal.objects.has_key(name), u'Object with given name already present!'
            self._internal.objects[name] = object

    def getAttribute(self, name):
        return self._internal.getAttributes()[name]

    def addAttribute(self, name, type, constraint=None, initialValue=None):
        if self._internal.isNodeRegisteredWithinEndpoint():
            raise CloudioModificationException(u'A CloudioRuntimeObject\'s structure can only be modified before' +
                                               u' it is registered within the endpoint!')

        # Create cloud.iO attribute
        attribute = CloudioAttribute()

        attribute._internal.setParent(self)
        attribute._internal.setName(name)
        attribute._internal.setType(type)

        # TODO Set attribute constraint
        #if constraint:
            #attribute._internal.setConstraint('???')

        if initialValue:
            attribute.setValue(initialValue)

        assert not self._internal._attributes.has_key(name), u'Attribute with given name already present!'
        self._internal._attributes[name] = attribute

        return attribute

# TODO Create and implement CloudioRuntimeObjectBuilder class
