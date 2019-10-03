#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example shows how to connect PIPython via socket."""

from pipython.gcscommands import GCSCommands
from pipython.gcsmessages import GCSMessages
from pipython.interfaces.pisocket import PISocket

IPADDR = '192.168.90.166'


def main():
    """Connect controller via socket on port 50000."""
    with PISocket(host=IPADDR, port=50000) as gateway:
        print('interface: {}'.format(gateway))
        messages = GCSMessages(gateway)
        pidevice = GCSCommands(messages)
        print('connected: {}'.format(pidevice.qIDN().strip()))


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    main()
