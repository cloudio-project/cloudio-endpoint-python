# -*- coding: utf-8 -*-

from exceptions import RuntimeError
from cloudio_node import CloudioNode
from cloudio_object import CloudioObject

class CloudioRuntimeNode(CloudioNode):
    """The CloudioAdLibNode class allows to create the structure of a cloud.iO node at runtime.

    It is in contrast with the CloudioNode class which uses a static model.
    """
    def __init__(self):
        super(CloudioRuntimeNode, self).__init__()

    def getObjects(self):
        return self.objects

    def addObject(self, name, clsOrObject):
        """Adds an object (or an object of the given class) with the given name to the runtime node."""
        if self.isNodeRegisteredWithinEndpoint():
            raise RuntimeError(u'A CloudioRuntimeNode\'s structure can only be modified before it is registered within' +
                               u' the endpoint!')

        # Check if parameter is a class
        if not isinstance(clsOrObject, CloudioObject):
            # Create an object of that class
            cls = clsOrObject
            obj = cls()         # Create an object of that class
            self.addObject(name, obj)
            return obj
        else:
            # We have an CloudioObject to add to the node
            object = clsOrObject
            object._internal.setParentObjectContainer(self)
            object._internal.setName(name)

            # Add object to the objects container
            assert not self.objects.has_key(name), u'Object with given name already present!'
            self.objects[name] = object

    def declareImplementedInterface(self, interfaceName):
        """Declares that the node implements the given interface.

        Note that you have to declare all implemented
        interfaces actually before the node is added to the endpoint, otherwise a runtime exception will be
        thrown.
        """
        if self.isNodeRegisteredWithinEndpoint():
            raise RuntimeError(u'Node is already registered within an endpoint, declaring implemented' +
                               u' interfaces is only possible as long as the node is not online' +
                               u' (registered within endpoint)!')

        if not self.getInterfaces().has_key(interfaceName):
            self.getInterfaces()[interfaceName]

    def declareImplementedInterfaces(self, interfaceNames):
        for interfaceName in interfaceNames:
            self.declareImplementedInterface(interfaceName)


# TODO Create and implement CloudioRuntimeNodeBuilder class
