# -*- coding: utf-8 -*-

from cloudio.endpoint.node import CloudioNode
from cloudio.endpoint.object import CloudioObject


class CloudioRuntimeNode(CloudioNode):
    """The CloudioRuntimeNode class allows to create the structure of a cloud.iO node at runtime.

    It is in contrast with the CloudioNode class which uses a static model.
    """

    def __init__(self):
        super(CloudioRuntimeNode, self).__init__()

    def get_objects(self):
        return self.objects

    def add_object(self, name, cls_or_object):
        """Adds an object (or an object of the given class) with the given name to the runtime node.
        """
        if self.is_node_registered_within_endpoint():
            raise RuntimeError('A CloudioRuntimeNode\'s structure can only be modified before it '
                               'is registered within the endpoint!')

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
            assert name not in self.objects, 'Object with given name already present!'
            self.objects[name] = obj
            return obj

    def declare_implemented_interface(self, interface_name):
        """Declares that the node implements the given interface.

        Note that you have to declare all implemented
        interfaces actually before the node is added to the endpoint, otherwise a runtime exception will be
        thrown.
        """
        if self.is_node_registered_within_endpoint():
            raise RuntimeError('Node is already registered within an endpoint, declaring implemented' +
                               ' interfaces is only possible as long as the node is not online' +
                               ' (registered within endpoint)!')

        if interface_name not in self.interfaces:
            self.interfaces.append(interface_name)

    def declare_implemented_interfaces(self, interface_names):
        for interfaceName in interface_names:
            self.declare_implemented_interface(interfaceName)

    def to_json(self, encoder):
        """Pick out the attributes we want to store / publish.
        """
        attrDict = {}

        if hasattr(self, 'objects') and len(self.objects) > 0:
            attrDict['objects'] = self.objects

        attrDict['implements'] = self.interfaces;

        return encoder.default(attrDict)

    def get_interfaces(self):
        return self.interfaces

    def remove_interface(self, interface:str):
        if interface in self.interfaces:
            self.interfaces.remove(interface)
            return True
        else:
            return False

    def add_interface(self, interface:str):
        self.interfaces.append(interface)

# TODO Create and implement CloudioRuntimeNodeBuilder class
