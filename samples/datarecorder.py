#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This example shows how to use the data recorder and plot the data."""

try:
    from matplotlib import pyplot
except ImportError:
    pyplot = None

from pipython import GCSDevice, datarectools, pitools

CONTROLLERNAME = 'C-884'
STAGES = ('M-122.2DD',)  # connect stages to axes
REFMODE = ('FRF',)  # reference the connected stages

NUMVALUES = 1024  # number of data sets to record as integer
RECRATE = 2000  # number of recordings per second, i.e. in Hz


def main():
    """Connect device, set up stage and read and display datarecorder data."""
    with GCSDevice(CONTROLLERNAME) as pidevice:
        pidevice.InterfaceSetupDlg(key='sample')
        print('connected: {}'.format(pidevice.qIDN().strip()))
        print('initialize connected stages...')
        pitools.startup(pidevice, STAGES, REFMODE)
        header, data = readdatarecorder(pidevice)
        showdata(header, data)


def readdatarecorder(pidevice):
    """Set up data recorder, move stage and read data of 2 tables for first axis.
    @type pidevice : pipython.gcscommands.GCSCommands
    @return : Tuple of (header, data), see qDRR command.
    """
    drec = datarectools.Datarecorder(pidevice)
    drec.numvalues = NUMVALUES
    drec.samplefreq = RECRATE
    print('data recorder rate: {:.2f} Hz'.format(drec.samplefreq))
    drec.options = (datarectools.RecordOptions.ACTUAL_POSITION_2, datarectools.RecordOptions.COMMANDED_POSITION_1)
    drec.sources = pidevice.axes[0]
    drec.trigsources = datarectools.TriggerSources.POSITION_CHANGING_COMMAND_1
    drec.arm()
    print('move stage on axis {}...'.format(pidevice.axes[0]))
    pidevice.MVR(pidevice.axes[0], 0.1)
    return drec.getdata()


def showdata(header, data):
    """Show 'data' of two record tables in a matplotlib plot.
    @param header : Header information from qDRR() as dictionary.
    @param data : Datarecorder data as two columns list of floats.
    """
    if pyplot is None:
        print('matplotlib is not installed')
        return
    timescale = [header['SAMPLE_TIME'] * i for i in range(len(data[0]))]
    pyplot.plot(timescale, data[0], color='red')
    pyplot.plot(timescale, data[1], color='blue')
    pyplot.xlabel('time (s)')
    pyplot.ylabel(', '.join((header['NAME0'], header['NAME1'])))
    pyplot.title('Datarecorder data over time')
    pyplot.grid(True)
    pyplot.show()


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    main()
