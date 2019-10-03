#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Interface class to communicate with a PI device."""

from abc import ABCMeta, abstractmethod, abstractproperty

__signature__ = 0x6b866167d51d215a461245822a9cf4d6


class PIGateway(object):
    """Interface (in terms of "base class") to communicate with a PI device.
    Members should log an according debug mesage.
    """

    __metaclass__ = ABCMeta

    def __str__(self):
        """Return class name with according parameter(s).
        e.g. "return 'GCSDll(%s)' % self.__dllpath"
        """
        raise NotImplementedError()

    @abstractproperty
    def connectionid(self):
        """Get ID of current connection as integer."""
        raise NotImplementedError()

    @abstractmethod
    def send(self, msg):
        """Send a GCS command to the device, do not query error from device.
        @param msg : GCS command as string with trailing line feed character.
        """
        raise NotImplementedError()

    @abstractproperty
    def answersize(self):
        """Get the size of an answer to a GCS query command as integer."""
        raise NotImplementedError()

    def getanswer(self, bufsize):
        """Get the answer to a GCS query command.
        @param bufsize : Size of the answer in number of characters as integer.
        @return : Answer as string.
        """
        raise NotImplementedError()
