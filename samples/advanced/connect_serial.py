#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example shows how to connect PIPython via serial port."""

import sys

from pipython.gcscommands import GCSCommands
from pipython.gcsmessages import GCSMessages
from pipython.interfaces.piserial import PISerial


def main():
    """Connect controller via first serial port with 115200 baud."""
    if sys.platform in ('linux', 'linux2', 'darwin'):
        port = '/dev/ttyS0'  # use '/dev/ttyUSB0' for FTDI-USB connections
    else:
        port = 'COM1'
    with PISerial(port=port, baudrate=115200) as gateway:
        print('interface: {}'.format(gateway))
        messages = GCSMessages(gateway)
        pidevice = GCSCommands(messages)
        print('connected: {}'.format(pidevice.qIDN().strip()))


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    main()
