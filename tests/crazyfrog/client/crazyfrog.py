# -*- coding: utf-8 -*-

import os
import sys
import time
import math
import logging
import json

from cloudio.common.utils import path_helpers
from cloudio.common.utils import datetime_helpers
from cloudio.common.mqtt import MqttConnectOptions, MqttReconnectClient

logging.getLogger(__name__).setLevel(logging.INFO)


class CrazyFrogClient(object):
    """A cloud.iO client connecting to CrazyFrog endpoint represented in the cloud.
    """

    log = logging.getLogger(__name__)

    def __init__(self, config_file):
        self._isRunning = True
        self._interval = 0.10  # Every 100 milliseconds
        self._isConnected = False

        config = self.parse_config_file(config_file)

        self._qos = 0

        self._endPointName = 'CrazyFrogEndpoint'
        self._nodeName = 'CrazyFrog'

        self.log.info('Starting CrazyFrog client...')

        self.connectOptions = MqttConnectOptions()

        self.connectOptions.caFile = path_helpers.prettify(config['cloudio']['cert'])
        self.connectOptions.username = config['cloudio']['username']
        self.connectOptions.password = config['cloudio']['password']

        self._client = MqttReconnectClient(config['cloudio']['host'],
                                           client_id=self._endPointName + '-client-',
                                           clean_session=True,
                                           options=self.connectOptions)

        # Register callback method for connection established
        self._client.set_on_connected_callback(self.on_connected)
        # Register callback method to be called when receiving a message over MQTT
        self._client.set_on_message_callback(self.on_message)

        self._client.start()

        self.wait_until_connected()

    def close(self):
        self._isRunning = False
        self._client.stop()

    @staticmethod
    def parse_config_file(config_file):

        from configobj import ConfigObj

        config = None

        path_config_file = path_helpers.prettify(config_file)

        if path_config_file and os.path.isfile(path_config_file):
            config = ConfigObj(path_config_file)

        if config:
            # Check if most important configuration parameters are present
            assert 'cloudio' in config, 'Missing group \'cloudio\' in config file!'

            assert 'host' in config['cloudio'], 'Missing \'host\' parameter in cloudio group!'
            assert 'cert' in config['cloudio'], 'Missing \'cert\' parameter in cloudio group!'
            assert 'username' in config['cloudio'], 'Missing \'username\' parameter in cloudio group!'
            assert 'password' in config['cloudio'], 'Missing \'password\' parameter in cloudio group!'
        else:
            sys.exit('Error reading config file')

        return config

    def wait_until_connected(self):
        while not self.is_connected():
            time.sleep(0.2)

    def is_connected(self):
        return self._isConnected

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._isConnected = True
            self._subscribe_to_updated_commands()

    def on_connected(self):
        self._isConnected = True
        self._subscribe_to_updated_commands()

    def on_disconnect(self, client, userdata, rc):
        self.log.info('Disconnect: ' + str(rc))

    def on_message(self, client, userdata, msg):
        print('{} received: {}'.format(self.__class__.__name__, msg.topic))

    def _subscribe_to_updated_commands(self):
        (result, mid) = self._client.subscribe('@update/' + self._endPointName + '/#', 1)
        return True if result == self._client.MQTT_ERR_SUCCESS else False

    def set_triangle(self, new_identification):
        topic = '@set/' + self._endPointName + '/nodes/' + self._nodeName + \
                '/objects/parameters/attributes/_triangle'

        payload = {
            'timestamp': datetime_helpers.getCurrentTimestamp(),
            'value': new_identification
        }
        self._client.publish(topic, json.dumps(payload), qos=self._qos)

    def execute(self):
        while self._isRunning:
            secs = time.time()
            frequency = 1.0 / 10  # [Hz]
            # https://en.wikipedia.org/wiki/Triangle_wave
            triangle_value = 10 * 2 / math.pi * math.asin(math.sin(2.0 * math.pi * frequency * secs))
            print('Updating triangle value: {0:0.2f}'.format(triangle_value))
            self.set_triangle(triangle_value)
            time.sleep(self._interval)
