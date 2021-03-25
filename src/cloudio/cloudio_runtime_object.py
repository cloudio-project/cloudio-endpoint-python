# -*- coding: utf-8 -*-

from cloudio.exception.cloudio_modification_exception import CloudioModificationException
from .cloudio_object import CloudioObject
from .cloudio_attribute import CloudioAttribute
from .cloudio_attribute_constraint import CloudioAttributeConstraint

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
            assert not name in self._internal.objects, u'Object with given name already present!'
            self._internal.objects[name] = object

    def getAttribute(self, name):
        return self._internal.getAttributes()[name]

    def addAttribute(self, name, type, constraint=None, initialValue=None):
        if self._internal.isNodeRegisteredWithinEndpoint():
            raise CloudioModificationException(u'A CloudioRuntimeObject\'s structure can only be modified before' +
                                               u' it is registered within the endpoint!')

        # Create cloud.iO attribute
        attribute = CloudioAttribute()

        attribute.setParent(self)
        attribute.setName(name)
        attribute.set_type(type)

        # Set attribute constraint
        if constraint:
            if isinstance(constraint, CloudioAttributeConstraint):
                attribute.setConstraint(constraint)
            else:
                assert isinstance(constraint, str) or isinstance(constraint, unicode), 'Wrong type'
                attribute.setConstraint(CloudioAttributeConstraint(constraint))
        else:
            attribute.setConstraint(CloudioAttributeConstraint('Invalid'))

        if initialValue:
            attribute.setValue(initialValue)

        assert not name in self._internal._attributes, u'Attribute with given name already present!'
        self._internal._attributes[name] = attribute

        return attribute

    def to_json(self, encoder):
        """Pick out the attributes we want to store / publish.
        """

        # Noting to encode here. Delegate job further to
        # internal object
        return encoder.default(self._internal)

# TODO Create and implement CloudioRuntimeObjectBuilder class
