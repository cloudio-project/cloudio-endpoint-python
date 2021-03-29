# -*- coding: utf-8 -*-

from cloudio.endpoint.exception.cloudio_modification_exception import CloudioModificationException
from cloudio.endpoint.object import CloudioObject
from cloudio.endpoint.attribute import CloudioAttribute
from cloudio.endpoint.attribute.constraint import CloudioAttributeConstraint


class CloudioRuntimeObject(CloudioObject):
    def __init__(self):
        super(CloudioRuntimeObject, self).__init__()

    def get_object(self, name):
        """Returns the object with the given name or null if no object with the given name is part of the object.
        """
        return self._internal.objects[name]

    def add_object(self, name, cls_or_object):
        """Adds an object (or an object of the given class) with the given name to the runtime object."""
        if self._internal.is_node_registered_within_endpoint():
            raise CloudioModificationException('A CloudioRuntimeObject\'s structure can only be modified before' +
                                               ' it is registered within the endpoint!')

        # Check if parameter is a class
        if not isinstance(cls_or_object, CloudioObject):
            # Create an object of that class
            cls = cls_or_object
            obj = cls()  # Create an object of that class
            self.add_object(name, obj)
            return obj
        else:
            # We have an CloudioObject to add to the node
            obj = cls_or_object
            obj._internal.set_parent_object_container(self)
            obj._internal.set_name(name)

            # Add object to the objects container
            assert name not in self._internal.objects, 'Object with given name already present!'
            self._internal.objects[name] = obj

    def get_attribute(self, name):
        return self._internal.get_attributes()[name]

    def add_attribute(self, name, atype, constraint=None, initial_value=None):
        if self._internal.is_node_registered_within_endpoint():
            raise CloudioModificationException('A CloudioRuntimeObject\'s structure can only be modified before' +
                                               ' it is registered within the endpoint!')

        # Create cloud.iO attribute
        attribute = CloudioAttribute()

        attribute.set_parent(self)
        attribute.set_name(name)
        attribute.set_type(atype)

        # Set attribute constraint
        if constraint:
            if isinstance(constraint, CloudioAttributeConstraint):
                attribute.set_constraint(constraint)
            else:
                assert isinstance(constraint, str), 'Wrong type'
                attribute.set_constraint(CloudioAttributeConstraint(constraint))
        else:
            attribute.set_constraint(CloudioAttributeConstraint('Invalid'))

        if initial_value:
            attribute.set_value(initial_value)

        assert name not in self._internal._attributes, 'Attribute with given name already present!'
        self._internal._attributes[name] = attribute

        return attribute

    def to_json(self, encoder):
        """Pick out the attributes we want to store / publish.
        """

        # Noting to encode here. Delegate job further to
        # internal object
        return encoder.default(self._internal)

# TODO Create and implement CloudioRuntimeObjectBuilder class
