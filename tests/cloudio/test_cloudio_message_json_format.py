#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import unittest
from tests.cloudio.paths import update_working_directory

update_working_directory()  # Needed when: 'pipenv run python -m unittest tests/cloudio/{this_file}.py'


class TestCloudioMessageFormatJson(unittest.TestCase):
    """Tests message json format.
    """

    log = logging.getLogger(__name__)

    def test_deserialize_attribute(self):
        from cloudio.endpoint.message_format.json_format import JsonMessageFormat
        from cloudio.endpoint.attribute import CloudioAttribute

        attribute_bool = CloudioAttribute()
        attribute_bool.set_type(bool)

        attribute_float = CloudioAttribute()
        attribute_float.set_type(float)

        data_dict = {'timestamp': 8888,
                     'value': 'true'
                     }

        data = json.dumps(data_dict)

        m_format = JsonMessageFormat()

        # Deserialize to bool
        m_format.deserialize_attribute(data, attribute_bool)

        # Conversion from value type string to attribute type float should raise
        # a value exception
        with self.assertRaises(ValueError):
            # Deserialize to float
            m_format.deserialize_attribute(data, attribute_float)


if __name__ == '__main__':
    # Enable logging
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    unittest.main()
