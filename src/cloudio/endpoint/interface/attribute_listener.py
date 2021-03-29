# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class CloudioAttributeListener(object):
    """
    This interface enables an application object to get notified as soon as there was a new value set to an attribute.
    If the change was set from the local application or from the cloud does not matter. This means that even on
    attributes with a @Measure constraint, you can add listeners in order to get notified about the applications own
    changes to the data model. This can be handy if in addition to the cloud, there is a local UI and application logic.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def attribute_has_changed(self, attribute):
        """This method is called upon an attribute has been changed.

        :param attribute Attribute that has changed.
        """
        pass
