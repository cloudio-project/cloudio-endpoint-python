# -*- coding: utf-8 -*-

import logging

from cloudio.endpoint.interface.attribute_listener import CloudioAttributeListener

logging.getLogger(__name__).setLevel(logging.INFO)


class VacuumCleaner(CloudioAttributeListener):
    """Class representing the 'real' vacuum cleaner.
    """

    log = logging.getLogger(__name__)

    def __init__(self):
        self.cloudioNode = None

        # The following attributes will be initialized by the cloud.io node (see 'config/vacuum-cleaner-model.xml')
        # They are added here to make the code interpreter happy
        self._identification = None
        self._powerOn = None
        self._throughput = None
        self._operatingMode = None

    def set_cloudio_buddy(self, cloudio_node):
        self.cloudioNode = cloudio_node

        assert self.cloudioNode, 'Cloudio node must be valid!'

        cloudio_parameter_object = self.cloudioNode.find_object(['Parameters',
                                                                'objects'])

        for attributeName, cloudioAttribute in cloudio_parameter_object.get_attributes().items():
            self._create_attribute(attributeName, cloudioAttribute)
            cloudioAttribute.add_listener(self)

    def _create_attribute(self, attribute_name, cloudio_attribute):
        """

        :param attribute_name: The attribute name given by cloud.iO
        :type attribute_name: str
        :param cloudio_attribute: The cloud.iO attribute
        :return:
        """
        internal_attribute_name = self._convert_to_internal_attribute_name(attribute_name)

        setattr(self, internal_attribute_name, cloudio_attribute.get_value())

    @staticmethod
    def _convert_to_internal_attribute_name(cloudio_attribute_name):
        internal_attribute_name = cloudio_attribute_name
        if cloudio_attribute_name.startswith('set'):
            # internal_attribute_name = '_' + cloudio_attribute_name[4:4 + 1].lower() + cloudio_attribute_name[5:]
            internal_attribute_name = cloudio_attribute_name[3:]     # Remove 'set'
            words = list(filter(None, internal_attribute_name.split('_')))
            internal_attribute_name = ''.join((map(lambda x: x.capitalize(), words)))

            internal_attribute_name = internal_attribute_name[0].lower() + internal_attribute_name[1:]
            internal_attribute_name = '_' + internal_attribute_name

        return internal_attribute_name

    def attribute_has_changed(self, attribute):
        """This method gets called when an attribute changes.

        CloudioAttributeListener interface implementation.

        Used to get informed about attribute value changes in the cloud
        representation of the node/device.

        :param attribute Attribute that has changed.
        """
        internal_attribute_name = self._convert_to_internal_attribute_name(attribute.get_name())
        print('VacuumCleaner attr changed: ' + str(attribute.get_value()))

        # Check if we have an attribute with the same name
        if hasattr(self, internal_attribute_name):
            setattr(self, internal_attribute_name, attribute.get_value())
        else:
            self.log.warning('Attribute \'' + internal_attribute_name + '\' not found in ' + self.__class__.__name__)
