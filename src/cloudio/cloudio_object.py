# -*- coding: utf-8 -*-

import types
from .interface.object_container import CloudioObjectContainer
from .interface.attribute_container import CloudioAttributeContainer
from .exception.invalid_cloudio_attribute_exception import InvalidCloudioAttributeException
from .exception.cloudio_modification_exception import CloudioModificationException
from .cloudio_attribute import CloudioAttribute
from .topicuuid import TopicUuid


class CloudioObject(object):
    """Base class for all cloud.iO objects.

    An object can either contain attributes (CloudioAttribute, @StaticAttribute) or child
    objects. Using this it is possible to create data models with a great flexibility.

    An object can be annotated with the @Conforms annotation to conform to a cloud.io class. A class in cloud.io is just
    a scheme what attributes and child objects an object has to have. An object is conform to such a scheme if it
    matches exactly the structure of the class. It can not contain more attributes or child objects, then it would be
    not anymore conform to that class.
    """
    def __init__(self):
        super(CloudioObject, self).__init__()
        self._internal = _InternalObject(self)

    def get_name(self):
        return self._internal.get_name()

    def set_name(self, name):
        self._internal.set_name(name)

    def find_attribute(self, location):
        return self._internal.find_attribute(location)

    def find_object(self, location):
        return self._internal.find_object(location)

    def get_attributes(self):
        return self._internal.get_attributes()

    def attribute_has_changed_by_endpoint(self, attribute):
        self._internal.attribute_has_changed_by_endpoint(attribute)

    def attribute_has_changed_by_cloud(self, attribute):
        self._internal.attribute_has_changed_by_cloud(attribute)

    def is_node_registered_within_endpoint(self):
        return self._internal.is_node_registered_within_endpoint()

    def get_parent_object_container(self):
        return self._internal.get_parent_object_container()


class _InternalObject(CloudioObjectContainer, CloudioAttributeContainer):

    def __init__(self, external_object):
        super(_InternalObject, self).__init__()
        self._externalObject = external_object
        self.parent = None      # type: CloudioObjectContainer or None
        self.name = None        # type: str or None
        self.conforms = None
        self.objects = {}
        self._attributes = {}
        self._staticAttributesAdded = False

        # Check each field of the actual CloudioObject object.
#        for field in dir(external_object):
#            # Check if it is an attribute and go get it
#            attr = getattr(external_object, field)
#           if attr:
#               if isinstance(attr, CloudioObject):
#                  print('Got an attribute based on an CloudioObject class')
#               elif type(field) == CloudioAttribute:
#                   print('Got an attribute based on an CloudioAttribute class')
#               else:
#                   print('Got an attribute with non-relevant type')

    def get_external_object(self):
        return self._externalObject

    ######################################################################
    # Interface implementations
    #
    def get_uuid(self):
        # TODO Store topic uuid as attribute
        return TopicUuid(self)

    def get_name(self):
        return self.name

    def set_name(self, name):
        # If the object already has a name (we are renaming the object)
        # then fail with a runtime exception.
        if self.name:
            raise CloudioModificationException('The Object has already a name (Renaming objects is forbidden)!')

        # Set the local name
        self.name = name

    def attribute_has_changed_by_endpoint(self, attribute):
        if self.parent:
            self.parent.attribute_has_changed_by_endpoint(attribute)

    def attribute_has_changed_by_cloud(self, attribute):
        if self.parent:
            self.parent.attribute_has_changed_by_cloud(attribute)

    def is_node_registered_within_endpoint(self):
        return self.parent and self.parent.is_node_registered_within_endpoint()

    def get_objects(self):
        return self.objects

    def set_parent_object_container(self, object_container):
        # If the object already has a parent (we are moving the object)
        # then fail with a runtime exception.
        if self.parent:
            raise CloudioModificationException('The parent of an Object can never be changed ' +
                                               '(Objects can not be moved)!')

        # Set the parent
        self.parent = object_container

    def get_parent_node_container(self):
        return None

    def get_parent_object_container(self):
        return self.parent

    def set_parent_node_container(self, node_container):
        raise CloudioModificationException('As this is not a node, it can not be embedded into a node container!')

    def find_attribute(self, location) -> CloudioAttribute or None:
        """Searches for an attribute.

        :param location: List containing the 'topic levels' constructed out of the topic uuid identifying the attribute.
        :type location [str]
        :return: The cloudio object found or None
        """
        if location:
            if len(location) > 0:
                if location[-1] == 'objects':  # Compare with last element (peek element)
                    location.pop()     # Remove last item
                    if len(location) > 0:
                        if location[-1] in self.get_objects():
                            obj = self.get_objects()[location.pop()]
                            if obj:
                                return obj.find_attribute(location)
                elif location[-1] == 'attributes':
                    self.get_attributes()    # Update attributes list
                    location.pop()         # Remove last item
                    if len(location) > 0:
                        if location[-1] in self.get_attributes():
                            attribute = self.get_attributes()[location.pop()]
                            if attribute:
                                return attribute
        return None

    def find_object(self, location):
        """Searches for an object.

        :param location: List containing the 'topic levels' constructed out of the topic uuid identifying the object.
        :type location [str]
        :return: The cloudio object found or None
        """
        if location:
            if len(location) > 0:
                if location[-1] == 'objects':  # Compare with last element (peek element)
                    location.pop()     # Remove last item
                    if len(location) > 0:
                        if location[-1] in self.get_objects():
                            obj = self.get_objects()[location.pop()]
                            return obj
                elif location[-1] == 'attributes':
                    obj = self.get_attributes()       # Update attributes list
                    location.pop()         # Remove last item
                    return obj
        return None

    def get_attributes(self):
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
                    if isinstance(attr, bool) or \
                       isinstance(attr, int) or \
                       isinstance(attr, float) or \
                       isinstance(attr, bytes) or \
                       isinstance(attr, str):

                        if field not in ('__module__', '__doc__'):  # Some excludes:
                            attribute = CloudioAttribute()
                            attribute.set_constraint('static')
                            attribute.set_name(field)
                            attribute.set_parent(self)
                            attribute.set_static_value(attr)

                            topicUuid = attribute.get_uuid().to_string()
                            if topicUuid and topicUuid not in self._attributes:
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

        if self.conforms is not None and len(self.conforms) > 0:
            attrDict['conforms'] = self.conforms

        if hasattr(self, 'objects') and len(self.objects) > 0:
            attrDict['objects'] = self.objects

        if hasattr(self, '_attributes') and len(self._attributes) > 0:
            attrDict['attributes'] = self._attributes

        return encoder.default(attrDict)

    ######################################################################
    # Private methods
    #
    @staticmethod
    def _get_conforms():
        return None

    def _set_conforms(self, data_class):
        pass
