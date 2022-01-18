# -*- coding: utf-8 -*-

import logging
import os
import traceback
from xml.dom import minidom

from cloudio.common.utils import path_helpers
from cloudio.endpoint import CloudioEndpoint
from cloudio.endpoint.runtime.node import CloudioRuntimeNode
from cloudio.endpoint.runtime.object import CloudioRuntimeObject

# Enable logging
logging.getLogger(__name__).setLevel(logging.INFO)


class VacuumCleanerConnector(object):
    """Creates the cloud.iO endpoint according to the model file.

    After creation the endpoint goes online and is available in the cloud.
    """
    log = logging.getLogger(__name__)

    def __init__(self, cloudio_endpoint_name, locations: str or list = None):
        self.endpoint = CloudioEndpoint(cloudio_endpoint_name, locations=locations)

    def get_endpoint_name(self):
        return self.endpoint.get_name()

    def create_model(self, xml_model_file):
        try:
            path_name = path_helpers.prettify(xml_model_file)

            self.log.info('Reading cloud.iO endpoint model from \'%s\'' % path_name)

            path_name = os.path.abspath(path_name)  # Convert to absolute path to make isfile() happy

            # Check if config file is present
            if os.path.isfile(path_name):
                # Parse XML config file
                xml_config_file = minidom.parse(path_name)

                if xml_config_file:
                    configList = xml_config_file.getElementsByTagName('config')
                    """:type : list of minidom.Element"""

                    for config in configList:
                        device_type_list = config.getElementsByTagName('deviceType')
                        """:type : list of minidom.Element"""

                        for device_type in device_type_list:
                            """:type : list of minidom.Element"""
                            print('Parsing elements for device: ' + device_type.getAttribute('typeId'))
                            self._parse_device_type_from_xml_dom_element(device_type)
            else:
                raise RuntimeError('Missing configuration file: %s' % path_name)

        except Exception:
            traceback.print_exc()

        # After the endpoint is fully created the presents can be announced
        self.endpoint.announce()

    def close(self):
        self.endpoint.close()

    def _parse_device_type_from_xml_dom_element(self, device_type):
        """Parses a device type from an xml dom element

        :param device_type:
        :type device_type: minidom.Element
        :return:
        """
        assert device_type.tagName == 'deviceType', 'Wrong DOM element name'

        node_name = device_type.getAttribute('typeId')
        cloudio_runtime_node = CloudioRuntimeNode()
        cloudio_runtime_node.declare_implemented_interface('NodeInterface')

        object_list = device_type.getElementsByTagName('object')
        """:type : list of minidom.Element"""
        for obj in object_list:
            object_name = obj.getAttribute('id')
            # Create cloud.iO object
            cloudio_runtime_object = CloudioRuntimeObject()
            # Add object to the node
            cloudio_runtime_node.add_object(object_name, cloudio_runtime_object)

            # Get the attributes for the object node
            attributeList = obj.getElementsByTagName('attribute')
            for attribute in attributeList:
                self._parse_attribute_from_xml_dom_element(cloudio_runtime_object, attribute)

        assert node_name, 'No node name given!'
        assert cloudio_runtime_node, 'No cloud.iO node object given!'
        self.endpoint.add_node(node_name, cloudio_runtime_node)

    @classmethod
    def _parse_attribute_from_xml_dom_element(cls, cloudio_runtime_object, attribute_element):
        """Parses an attribute from an xml dom element

        :param cloudio_runtime_object:
        :type cloudio_runtime_object: CloudioRuntimeObject
        :param attribute_element:
        :type attribute_element: minidom.Element
        :return:
        """
        assert attribute_element.tagName == 'attribute', 'Wrong DOM element name'

        the_name = attribute_element.getAttribute('id')
        str_type = attribute_element.getAttribute('template')
        str_constraint = attribute_element.getAttribute('constraint')

        # TODO Convert constraint from 'string' to CloudioAttributeConstraint

        the_type = None

        if str_type.lower() == 'bool' or str_type.lower() == 'boolean':
            the_type = bool
        elif str_type.lower() in ('short', 'long', 'integer'):
            the_type = int
        elif str_type.lower() == 'float' or str_type.lower() == 'double' or str_type.lower() == 'number':
            the_type = float
        elif str_type.lower() == 'str' or str_type.lower() == 'string':
            the_type = str

        assert the_type, 'Attribute type unknown or not set!'

        cloudio_runtime_object.add_attribute(the_name, the_type, str_constraint)
