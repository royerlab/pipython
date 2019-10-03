#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example helps you to get used to PIPython."""

from random import uniform

from pipython import GCSDevice, pitools

CONTROLLERNAME = 'C-863.11'
STAGES = ('M-111.1DG',)  # connect stages to axes
REFMODE = ('FNL',)  # reference the connected stages

# CONTROLLERNAME = 'C-884.DB'  # 'C-884' will also work
# STAGES = ('M-111.1DG', 'M-111.1DG', 'NOSTAGE', 'NOSTAGE')
# REFMODE = ('FNL', 'FNL')

# CONTROLLERNAME = 'E-709'
# STAGES = None  # this controller does not need a 'stages' setting
# REFMODE = None


def main():
    """Connect, setup system and move stages and display the positions in a loop."""

    # We recommend to use GCSDevice as context manager with "with".
    # The CONTROLLERNAME decides which PI GCS DLL is loaded. If your controller works
    # with the PI_GCS2_DLL (as most controllers actually do) you can leave this empty.

    with GCSDevice(CONTROLLERNAME) as pidevice:
        # InterfaceSetupDlg() is an interactive dialog. There are other methods to
        # connect to an interface without user interaction.

        pidevice.InterfaceSetupDlg(key='sample')
        # pidevice.ConnectRS232(comport=1, baudrate=115200)
        # pidevice.ConnectUSB(serialnum='123456789')
        # pidevice.ConnectTCPIP(ipaddress='192.168.178.42')

        # Controllers like C-843 and E-761 are connected via PCI.
        # pidevice.ConnectPciBoard(board=1)

        # Each PI controller supports the qIDN() command which returns an
        # identification string with a trailing line feed character which
        # we "strip" away.

        print('connected: {}'.format(pidevice.qIDN().strip()))

        # Show the version info which is helpful for PI support when there
        # are any issues.

        if pidevice.HasqVER():
            print('version info: {}'.format(pidevice.qVER().strip()))

        # In the module pipython.pitools there are some helper
        # functions to make using a PI device more convenient. The "startup"
        # function will initialize your system. There are controllers that
        # cannot discover the connected stages hence we set them with the
        # "stages" argument. The desired referencing method (see controller
        # user manual) is passed as "refmode" argument

        print('initialize connected stages...')
        pitools.startup(pidevice, stages=STAGES, refmode=REFMODE)

        # Now we query the allowed motion range of all connected stages.
        # GCS commands often return an (ordered) dictionary with axes/channels
        # as "keys" and the according values as "values".

        rangemin = list(pidevice.qTMN().values())
        rangemax = list(pidevice.qTMX().values())
        ranges = zip(rangemin, rangemax)

        # To make this sample a bit more vital we will move to five different
        # random targets in a loop.

        for _ in range(5):
            targets = [uniform(rmin, rmax) for (rmin, rmax) in ranges]
            print('move stages...')

            # The GCS commands qTMN() and qTMX() used above are query commands.
            # They don't need an argument and will then return all availabe
            # information, e.g. the limits for _all_ axes. With setter commands
            # however you have to specify the axes/channels. GCSDevice provides
            # a property "axes" which returns the names of all connected axes.
            # So lets move our stages...

            pidevice.MOV(pidevice.axes, targets)

            # To check the on target state of an axis there is the GCS command
            # qONT(). But it is more convenient to just call "waitontarget".

            pitools.waitontarget(pidevice)

            # GCS commands usually can be called with single arguments, with
            # lists as arguments or with a dictionary.
            # If a query command is called with an argument the keys in the
            # returned dictionary resemble the arguments. If it is called
            # without an argument the keys are always strings.

            positions = pidevice.qPOS(pidevice.axes)
            for axis in pidevice.axes:
                print('position of axis {} = {:.2f}'.format(axis, positions[axis]))

            # positions = pidevice.qPOS()
            # for axis in positions:
            #    print('position of axis {} = {.2f}'.format(axis, positions[axis]))

        print('done')


if __name__ == '__main__':
    # To see what is going on in the background you can remove the following
    # two hashtags. Then debug messages are shown. This can be helpful if
    # there are any issues.

    # import logging
    # logging.basicConfig(level=logging.DEBUG)

    main()
