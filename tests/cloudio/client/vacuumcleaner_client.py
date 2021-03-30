# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import json
import paho.mqtt.client as mqtt

from cloudio.common.utils import path_helpers
from cloudio.common.utils import datetime_helpers
from cloudio.common.mqtt import MqttConnectOptions, MqttReconnectClient

logging.getLogger(__name__).setLevel(logging.INFO)


class VacuumCleanerClient(object):
    """A cloud.iO client connecting to a vacuum cleaner represented in the cloud.
    """

    MQTT_ERR_SUCCESS = mqtt.MQTT_ERR_SUCCESS

    log = logging.getLogger(__name__)

    def __init__(self, config_file):
        self._isConnected = False
        self._useReconnectClient = True             # Chooses the MQTT client
        config = self.parse_config_file(config_file)

        self._qos = int(config['cloudio']['qos'])

        self._endPointName = config['endpoint']['name']
        self._nodeName = config['node']['name']

        self.log.info('Starting MQTT client...')

        if not self._useReconnectClient:
            self._client = mqtt.Client()

            self._client.on_connect = self.on_connect
            self._client.on_disconnect = self.on_disconnect
            self._client.on_message = self.on_message

            self._client.username_pw_set(config['cloudio']['username'], config['cloudio']['password'])
            self._client.connect(config['cloudio']['host'], port=int(config['cloudio']['port']), keepalive=60)
            self._client.loop_start()
        else:
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

    def close(self):
        if not self._useReconnectClient:
            self._client.disconnect()
        else:
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
            assert 'endpoint' in config, 'Missing group \'endpoint\' in config file!'
            assert 'node' in config, 'Missing group \'node\' in config file!'

            assert 'host' in config['cloudio'], 'Missing \'host\' parameter in cloudio group!'
            assert 'port' in config['cloudio'], 'Missing \'port\' parameter in cloudio group!'
            assert 'cert' in config['cloudio'], 'Missing \'cert\' parameter in cloudio group!'
            assert 'username' in config['cloudio'], 'Missing \'username\' parameter in cloudio group!'
            assert 'password' in config['cloudio'], 'Missing \'password\' parameter in cloudio group!'
            assert 'subscribe_topics' in config['cloudio'], 'Missing \'subscribe_topics\' parameter in cloudio group!'
            assert 'qos' in config['cloudio'], 'Missing \'qos\' parameter in cloudio group!'

            assert 'name' in config['endpoint'], 'Missing \'name\' parameter in endpoint group!'

            assert 'name' in config['node'], 'Missing \'name\' parameter in node group!'
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
        print('VacuumCleanerClient rxed: ' + msg.topic)

    def _subscribe_to_updated_commands(self):
        (result, mid) = self._client.subscribe('@update/' + self._endPointName + '/#', 1)
        return True if result == self.MQTT_ERR_SUCCESS else False

    def set_identification(self, new_identification):
        topic = '@set/' + self._endPointName + '/nodes/' + self._nodeName + \
                '/objects/Parameters/attributes/set_identification'

        payload = {
            'timestamp': datetime_helpers.getCurrentTimestamp(),
            'value': new_identification
        }
        self._client.publish(topic, json.dumps(payload), qos=self._qos)

    def set_power_on(self, power_state=True):
        topic = '@set/' + self._endPointName + '/nodes/' + self._nodeName + \
                '/objects/Parameters/attributes/set_power_on'

        payload = {
            'timestamp': datetime_helpers.getCurrentTimestamp(),
            'value': power_state
        }
        self._client.publish(topic, json.dumps(payload), qos=self._qos)

    def set_throughput(self, new_throughput_value):
        topic = '@set/' + self._endPointName + '/nodes/' + self._nodeName + \
                '/objects/Parameters/attributes/set_throughput'

        payload = {
            'timestamp': datetime_helpers.getCurrentTimestamp(),
            'value': new_throughput_value
        }
        self._client.publish(topic, json.dumps(payload), qos=self._qos)

    def set_operating_mode(self, new_operating_mode):
        topic = '@set/' + self._endPointName + '/nodes/' + self._nodeName + \
                '/objects/Parameters/attributes/set_operating_mode'

        payload = {
            'timestamp': datetime_helpers.getCurrentTimestamp(),
            'value': new_operating_mode
        }
        self._client.publish(topic, json.dumps(payload), qos=self._qos)
