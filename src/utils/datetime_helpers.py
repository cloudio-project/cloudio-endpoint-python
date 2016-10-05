# -*- coding: utf-8 -*-

import datetime

EPOCH = datetime.datetime.utcfromtimestamp(0)

def getCurrentTimestamp():
    """Creates a timestamp using the current date and time."""
    currentDateTime = datetime.datetime.utcnow()
    return _unixTimeMillis(currentDateTime)

def getTimestamp(dt):
    """Creates a timestamp using parameter dt.
    :param dt The datetime object to convert to a timestamp
    :type dt datetime
    """
    return _unixTimeMillis(dt)

def _unixTimeMillis(dt):
    """Converts a datetime object into unix time including milliseconds.
    :param dt The datetime object to convert.
    :type dt datetime
    """
    ut = int((dt - EPOCH).total_seconds()) * 1000
    ut += dt.microsecond/1000
    return ut