# -*- coding: utf-8 -*-

import os
import logging
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

    def __init__(self, cloudio_endpoint_name):
        self.endpoint = CloudioEndpoint(cloudio_endpoint_name)

    def getEndpointName(self):
        return self.endpoint.get_name()

    def createModel(self, xml_model_file):
        try:
            pathName = path_helpers.prettify(xml_model_file)

            self.log.info('Reading cloud.iO enpoint model from \'%s\'' % pathName)

            pathName = os.path.abspath(pathName)    # Convert to absolute path to make isfile() happy

            # Check if config file is present
            if os.path.isfile(pathName):
                # Parse XML config file
                xmlConfigFile = minidom.parse(pathName)

                if xmlConfigFile:
                    configList = xmlConfigFile.getElementsByTagName('config')
                    """:type : list of minidom.Element"""

                    for config in configList:
                        deviceTypeList = config.getElementsByTagName('deviceType')
                        """:type : list of minidom.Element"""

                        for deviceType in deviceTypeList:
                            """:type : list of minidom.Element"""
                            print('Parsing elements for device: ' + deviceType.getAttribute('typeId'))
                            self._parseDeviceTypeFromXmlDomElement(deviceType)
            else:
                raise RuntimeError('Missing configuration file: %s' % pathName)

        except Exception as e:
            traceback.print_exc()

        # After the endpoint is fully created the presents can be announced
        self.endpoint.announce()

    def close(self):
        self.endpoint.close()

    def _parseDeviceTypeFromXmlDomElement(self, deviceType):
        """Parses a device type from an xml dom element

        :param deviceType:
        :type deviceType: minidom.Element
        :return:
        """
        assert deviceType.tagName == 'deviceType', 'Wrong DOM element name'

        nodeName = deviceType.getAttribute('typeId')
        cloudioRuntimeNode = CloudioRuntimeNode()
        cloudioRuntimeNode.declare_implemented_interface('NodeInterface')

        objectList = deviceType.getElementsByTagName('object')
        """:type : list of minidom.Element"""
        for obj in objectList:
            objectName = obj.getAttribute('id')
            # Create cloud.iO object
            cloudioRuntimeObject = CloudioRuntimeObject()
            # Add object to the node
            cloudioRuntimeNode.add_object(objectName, cloudioRuntimeObject)

            # Get the attributes for the object node
            attributeList = obj.getElementsByTagName('attribute')
            for attribute in attributeList:
                self._parseAttributeFromXmlDomElement(cloudioRuntimeObject, attribute)

        assert nodeName, 'No node name given!'
        assert cloudioRuntimeNode, 'No cloud.iO node object given!'
        self.endpoint.add_node(nodeName, cloudioRuntimeNode)

    @classmethod
    def _parseAttributeFromXmlDomElement(cls, cloudioRuntimeObject, attributeElement):
        """Parses an attribute from an xml dom element

        :parame cloudioRuntimeObject:
        :type cloudioRuntimeObject: CloudioRuntimeObject
        :param attributeElement:
        :type attributeElement: minidom.Element
        :return:
        """
        assert attributeElement.tagName == 'attribute', 'Wrong DOM element name'

        theName = attributeElement.getAttribute('id')
        strType = attributeElement.getAttribute('template')
        strConstraint = attributeElement.getAttribute('constraint')

        # TODO Get options

        # TODO Convert constraint from 'string' to CloudioAttributeConstraint

        theType = None

        if strType.lower() == 'bool' or strType.lower() == 'boolean':
            theType = bool
        elif strType.lower() in ('short', 'long', 'integer'):
            theType = int
        elif strType.lower() == 'float' or strType.lower() == 'double' or strType.lower() == 'number':
            theType = float
        elif strType.lower() == 'str' or strType.lower() == 'string':
            theType = str

        assert theType, 'Attribute type unknown or not set!'

        cloudioRuntimeObject.add_attribute(theName, theType, strConstraint)

