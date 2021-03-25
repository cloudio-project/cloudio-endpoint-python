# -*- coding: utf-8 -*-

class CloudioAttributeConstraint(object):
    """Defines the different possible attribute constraints.
    """

    # The attribute is a static value and can't be changed during runtime.
    Static = 0

    # The attribute is a parameter that can be configured from the cloud and its value should be saved locally on
    # the "Endpoint". Note that the cloud.iO communication library will not save the value, it is the responsibility
    # of you to actually save the configuration to a persistent location.
    Parameter = 1

    # The attribute is a status.
    Status = 2

    # The attribute is a set point that can be changed from the cloud. Note that there is no guarantee that the value
    # of set points are stored within the "Endpoint" and might be initialized to the default value on the next power
    # cycle.
    SetPoint = 3

    # The attribute is a measure of any kind and can change at any time.
    Measure = 4

    # If unknown or not set.
    Invalid = -1

    def __init__(self, value):

        if isinstance(value, str):
            if value.lower() == 'static':
                self._value = self.Static
            elif value.lower() == 'parameter':
                self._value = self.Parameter
            elif value.lower() == 'status':
                self._value = self.Status
            elif value.lower() == 'setpoint':
                self._value = self.SetPoint
            elif value.lower() == 'measure':
                self._value = self.Measure
            elif value.lower() == 'invalid':
                self._value = self.Invalid
        elif isinstance(value, int):
            self._value = value
        else:
            self._value = self.Invalid

    def get_value(self):
        return self._value

    def to_string(self):
        if self._value == self.Static:
            return 'Static'
        elif self._value == self.Parameter:
            return 'Parameter'
        elif self._value == self.Status:
            return 'Status'
        elif self._value == self.SetPoint:
            return 'SetPoint'
        elif self._value == self.Measure:
            return 'Measure'
        else:
            return 'Invalid'

    def to_json(self, encoder):
        """Pick out the attributes we want to store / publish.
        """
        return self.to_string()
