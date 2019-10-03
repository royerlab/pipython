#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Provide access to the serial port. Requires the "pyserial" package (pip install pyserial)."""

from logging import debug
import serial

from pipython.interfaces.pigateway import PIGateway

__signature__ = 0xa6cabd9657e241e499e44acf9af4d02d


class PISerial(PIGateway):
    """Provide access to the serial port, can be used as context manager."""

    def __init__(self, port, baudrate):
        """Provide access to the serial port.
        @param port : Name of the serial port to use as string, e.g. "COM1" or "/dev/ttyS0".
        @param baudrate : Baud rate as integer.
        """
        debug('create an instance of PISerial(port=%s, baudrate=%s)', port, baudrate)
        self.__ser = serial.Serial(port=port, baudrate=baudrate)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __str__(self):
        return 'PISerial(port=%s, baudrate=%s)' % (self.__ser.port, self.__ser.baudrate)

    @property
    def connectionid(self):
        """Get ID of current connection as integer."""
        return 0

    def send(self, msg):
        """Send 'msg' to the serial port.
        @param msg : String to send.
        """
        debug('PISerial.send: %r', msg)
        self.__ser.write(msg)

    @property
    def answersize(self):
        """Return the number of characters currently in the input buffer as integer."""
        return self.__ser.inWaiting

    def getanswer(self, bufsize):
        """Return received data.
        @param bufsize : Number of bytes to return.
        @return : Answer as string.
        """
        answer = self.__ser.read(size=bufsize)
        debug('PISerial.getanswer: %r', answer)
        return answer

    def close(self):
        """Close serial port."""
        debug('PISerial.close: close connection to %s', self.__ser.port)
        self.__ser.close()
