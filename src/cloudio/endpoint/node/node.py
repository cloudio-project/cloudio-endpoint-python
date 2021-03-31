# -*- coding: utf-8 -*-

from cloudio.endpoint.interface.object_container import CloudioObjectContainer
from cloudio.endpoint.exception.cloudio_modification_exception import CloudioModificationException
from cloudio.endpoint.topicuuid import TopicUuid
from cloudio.endpoint.object import CloudioObject


class CloudioNode(CloudioObjectContainer):
    def __init__(self):
        super(CloudioNode, self).__init__()
        self.parent = None
        self.name = None
        self.interfaces = {}
        self.objects = {}           # type: dict[CloudioObject]

        self._update_cloudio_objects()

        # TODO Implement add to annotation
        self._add_implemented_interface_to_annotation()

    def _update_cloudio_objects(self):
        # Check each field of the actual node
        for field in dir(self):
            # Check if it is an attribute and ...
            attr = getattr(self, field)
            if attr:
                if isinstance(attr, CloudioObject):
                    print('Node: Got an attribute based on an CloudioObject class')

    def _add_implemented_interface_to_annotation(self):
        pass

    ######################################################################
    # Interface implementations
    #
    def get_uuid(self):
        return TopicUuid(self)

    def get_name(self):
        return self.name

    def set_name(self, name):
        # If the node already has a name (we are renaming the node)
        # then fail with a runtime exception.
        if self.name:
            raise CloudioModificationException('The node has already a name (Renaming objects is forbidden)!')

        # Set the local name
        self.name = name

    def get_objects(self):
        return self.objects

    def get_parent_node_container(self):
        return self.parent

    def set_parent_node_container(self, node_container):
        # If the object already has a parent (we are moving the object)
        # then fail with a runtime exception.
        if self.parent:
            raise CloudioModificationException('The parent of a Node can never be changed ' +
                                               '(Nodes can not be moved)!')

        # Set the parent
        self.parent = node_container

    def get_parent_object_container(self):
        return None

    def set_parent_object_container(self, object_container):
        raise CloudioModificationException('A node can not have an object container as parent!')

    def attribute_has_changed_by_endpoint(self, attribute):
        if self.parent:
            self.parent.attribute_has_changed_by_endpoint(attribute)

    def attribute_has_changed_by_cloud(self, attribute):
        if self.parent:
            self.parent.attribute_has_changed_by_cloud(attribute)

    def is_node_registered_within_endpoint(self):
        return self.parent and self.parent.is_node_registered_within_endpoint()

    def find_attribute(self, location):
        """Searches for an attribute.

        :param location: List containing the 'topic levels' constructed out of the topic uuid identifying the attribute.
        :type location [str]
        :return: The cloudio object found or None
        :rtype CloudioAttribute
        """
        if location:
            if len(location) > 0:
                if location[-1] == 'objects':      # Compare with the last element
                    location.pop()     # Remove last item (peek item)
                    if len(location) > 0:
                        if location[-1] in self.get_objects():
                            # Get object from container (dictionary) by key
                            obj = self.get_objects()[location.pop()]
                            if obj:
                                return obj.find_attribute(location)
        return None

    def find_object(self, location) -> CloudioObject or None:
        """Searches for object.

        :param location: List containing the 'topic levels' constructed out of the topic uuid identifying the attribute.
        :type location [str]
        :return: The cloudio object found or None
        """
        if location:
            if len(location) > 0:
                if location[-1] == 'objects':  # Compare with the last element
                    location.pop()  # Remove last item (peek item)
                    if len(location) > 0:
                        if location[-1] in self.get_objects():
                            # Get object from container (dictionary) by key
                            obj = self.get_objects()[location.pop()]
                            return obj
        return None
