# -*- coding: utf-8 -*-

import time
import math
from cloudio.endpoint import CloudioEndpoint
from cloudio.endpoint.interface import CloudioAttributeListener


class CrazyFrogEndpoint(CloudioAttributeListener):

    def __init__(self, cloudio_endpoint_name='CrazyFrogEndpoint'):
        super(CrazyFrogEndpoint, self).__init__()

        from cloudio.endpoint.attribute import CloudioAttribute

        self._isRunning = True
        self._interval = 0.5  # Every 500 milliseconds

        self._endpoint = CloudioEndpoint(cloudio_endpoint_name, locations='path:../config/')

        self._sinus = None  # type: CloudioAttribute or None

    def initialize(self):
        # Wait until connected to cloud.iO
        while not self._endpoint.isOnline():
            time.sleep(0.2)

        self._create_model()

    def _create_model(self):
        from cloudio.endpoint.runtime import CloudioRuntimeNode, CloudioRuntimeObject

        node = CloudioRuntimeNode()
        node.declare_implemented_interface('NodeInterface')

        # Create attribute 'properties/_sinus'. Changed locally by endpoint
        props = CloudioRuntimeObject()
        node.add_object('properties', props)

        self._sinus = props.add_attribute('_sinus', float, 'measure')

        # Create attribute 'parameters/_triangle'. Changed remotely by client
        params = CloudioRuntimeObject()
        node.add_object('parameters', params)
        self._triangle = params.add_attribute('_triangle', float, 'parameter')
        self._triangle.add_listener(self)

        self._endpoint.addNode('CrazyFrog', node)

    def exec(self):
        while self._isRunning:
            secs = time.time()
            frequency = 1.0 / 10  # [Hz]
            sinus_value = 10 * math.sin(2.0 * math.pi * frequency * secs)
            self._sinus.set_value(sinus_value)
            # print('Updating sinus value: {0:0.2f}'.format(self._sinus.get_value()))
            time.sleep(self._interval)

    def attribute_has_changed(self, attribute):
        """This method gets called when an attribute was updated from the cloud.

        CloudioAttributeListener interface implementation.

        :param attribute Attribute that has changed.
        """

        # print('{} attribute changed: {}'.format(self.__class__.__name__, str(attribute.get_value())))

        # Notify the cloud that attribute was changed
        attribute.set_value(attribute.get_value())
