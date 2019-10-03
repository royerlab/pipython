#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tools for setting up and using the data recorder of a PI device."""

from __future__ import print_function
from logging import debug, warning
from time import sleep, time

from pipython.pitools import FrozenClass

__signature__ = 0x5b021be6068b79913c1270289282b79

# seconds
SERVOTIMES = {
    'C-413K011': 0.00003333333,
    'C-663.11': 50E-6,
    'C-663.12': 50E-6,
    'C-702.00': 100E-6,
    'C-843': 410E-6,
    'C-863.11': 50E-6,
    'C-867.160': 50E-6,  # verified
    'C-867.260': 50E-6,  # verified
    'C-867.262': 50E-6,  # verified
    'C-867K016': 50E-6,  # verified
    'C-867.B0017': 100E-6,
    'C-867.B0019': 100E-6,
    'C-867.B024': 100E-6,
    'C-867.K0020': 100E-6,
    'C-867.OE': 50E-6,
    'C-867K021': 100E-6,
    'C-877': 100E-6,
    'C-880': 4096E-6,
    'C-884.4D': 50E-6,
    'C-884.4DB': 50E-6,
    'C-887': 20E-6,
    'E-710': 200E-6,
    'E-755': 200E-6,
    'E-861': 50E-6,
    'E-861.11C885': 50E-6,
    'E-871.1A1': 50E-6,
    'E-873': 50E-6,
    'E-873.1A1': 50E-6,
    'E-873.3QTU': 50E-6,
}

MAXNUMVALUES = {
    'C-413K011': 4096,
    'C-663.10C885': 1024,
    'C-663.11': 1024,
    'C-663.12': 1024,
    'C-702.00': 262144,
    'C-863.11': 1024,
    'C-867.160': 8192,  # verified
    'C-867.1U': 8192,  # verified
    'C-867.260': 8192,  # verified
    'C-867.262': 8192,  # verified
    'C-867K016': 8192,  # verified
    'C-867K028': 1024,  # verified
    'C-867K031': 8192,  # verified
    'C-867K036 APP': 1024,  # verified
    'C-867.2U': 8192,  # verified
    'C-867.2U2': 8192,  # verified
    'C-867.B0017': 8192,
    'C-867.B0019': 8192,
    'C-867.B024': 8192,
    'C-867.K0020': 8192,
    'C-867.OE': 1024,
    'C-867K021': 8192,
    'C-877': 1024,
    'C-877.1U11': 1024,  # verified
    'C-877.2U12': 1024,  # verified
    'C-884.4D': 8192,
    'C-884.4DB': 8192,
    'E-761': 8192,
    'E-861': 1024,
    'E-861.11C885': 1024,
    'E-871.1A1': 1024,
    'E-873': 1024,
    'E-873.1A1': 1024,
    'E-873.3QTU': 8192,
}


# Invalid class attribute name pylint: disable=C0103
# Too few public methods pylint: disable=R0903
class RecordOptions(object):
    """Defines for the kind of data to be recorded."""
    NOTHING_0 = 0
    COMMANDED_POSITION_1 = 1
    ACTUAL_POSITION_2 = 2
    POSITION_ERROR_3 = 3
    PIO_VALUE_4 = 4
    DIO_VALUE_5 = 5
    COMEDI_VALUE_6 = 6
    PIEZO_VOLTAGE_7 = 7
    TIMESTAMP_8 = 8
    INDEX_9 = 9
    TICKS_10 = 10
    DDL_OUTPUT_13 = 13
    OPENLOOP_INPUT_14 = 14
    PID_OUTPUT_15 = 15
    ANALOG_OUTPUT_16 = 16
    SENSOR_NORMALIZED_17 = 17
    SENSOR_FILTERED_18 = 18
    SENSOR_ELEC_LIN_19 = 19
    SENSOR_MECH_LIN_20 = 20
    TARGET_SLEWRATE_LIM_22 = 22
    TARGET_VELOCITY_23 = 23
    TARGET_ACCELERATION_24 = 24
    TARGET_JERK_25 = 25
    DI_VALUE_26 = 26
    DO_VALUE_27 = 27
    CTV_TARGET_VALUE_28 = 28
    CCV_CONTROL_VALUE_29 = 29
    CAV_ACTUAL_VALUE_30 = 30
    CCV_CURRENT_VALUE_31 = 31
    DRIFT_COMP_OFFSET_32 = 32
    HYBRID_MOTOR_VOLTAGE_33 = 33
    HYBRID_PIEZO_VOLTAGE_34 = 34
    SYSTEM_TIME_44 = 44
    COMMANDED_VELOCITY_70 = 70
    COMMANDED_ACCELERATION_71 = 71
    ACTUAL_VELOCITY_72 = 72
    MOTOR_OUTPUT_73 = 73
    KP_OF_AXIS_74 = 74
    KI_OF_AXIS_75 = 75
    KD_OF_AXIS_76 = 76
    SIGNAL_STATUS_REGISTER_80 = 80
    ANALOG_INPUT_81 = 81
    ACTIVE_PARAMETERSET_90 = 90
    ACTUAL_FREQUENCY_91 = 91
    P0_92 = 92
    DIA_93 = 93
    CURRENT_PHASE_A_100 = 100
    CURRENT_PHASE_B_101 = 101
    CURRENT_PHASE_C_102 = 102
    CURRENT_PHASE_D_103 = 103
    FIELD_ORIENTED_CONTROL_UD_105 = 105
    FIELD_ORIENTED_CONTROL_UQ_106 = 106
    FIELD_ORIENTED_CONTROL_ID_107 = 107
    FIELD_ORIENTED_CONTROL_IQ_108 = 108
    FIELD_ORIENTED_CONTROL_U_ALPHA_109 = 109
    FIELD_ORIENTED_CONTROL_U_BETA_110 = 110
    FIELD_ORIENTED_CONTROL_V_PHASE_111 = 111
    FIELD_ORIENTED_CONTROL_ANGLE_112 = 112
    FIELD_ORIENTED_CONTROL_ANGLE_FROM_POS_113 = 113
    FIELD_ORIENTED_CONTROL_ERROR_D_114 = 114
    FIELD_ORIENTED_CONTROL_ERROR_Q_115 = 115
    POSITION_CONTROL_OUT_120 = 120
    VELOCITY_CONTROL_OUT_121 = 121
    PILOT_CONTROL_OUT_122 = 122
    ACCELERATION_CONTROL_OUT_123 = 123
    LOW_PASS_FILTERED_VELOCITY_140 = 140
    ANALOG_IN_VALUE_141 = 141
    LOW_PASS_FILTERED_VELOCITY_ERROR_142 = 142
    ACTUAL_ACCELERATION_143 = 143
    LOW_PASS_FILTERED_ACCELERATION_ERROR_144 = 144
    TW8_SINE_REGISTER_145 = 145
    TW8_COSINE_REGISTER_146 = 146
    FAST_ALIGNMENT_INPUT_CHANNEL_150 = 150
    FAST_ALIGNMENT_PROCESS_REGISTER_151 = 151
    FAST_ALIGNMENT_GS_RESULT_ROUTINE_152 = 152
    FAST_ALIGNMENT_GS_WEIGHT_ROUTINE_153 = 153
    FAST_ALIGNMENT_GS_AMPLITUDE_ROUTINE_154 = 154
    FAST_ALIGNMENT_FINISHED_FLAG_155 = 155
    FAST_ALIGNMENT_GRADIENT_SCAN_PHASE_ROUTINE_156 = 156


class TriggerSources(object):  # Too few public methods pylint: disable=R0903
    """Defines for sources that can trigger data recording."""
    DEFAULT_0 = 0
    POSITION_CHANGING_COMMAND_1 = 1
    NEXT_COMMAND_WITH_RESET_2 = 2
    EXTERNAL_TRIGGER_3 = 3
    TRIGGER_IMMEDIATELY_4 = 4
    DIO_CHANNEL_5 = 5
    POS_CHANGING_WITH_RESET_6 = 6
    SMO_COMMAND_WITH_RESET_7 = 7
    COMEDI_CHANNEL_8 = 8
    WAVE_GENERATOR_9 = 9


def __getopt(name, enumclass):
    """Return item of 'enumclass' which name parts start with 'name'.
     @param name : Short name of item, e.g. "CUR_POS". Case insensitive, separated by "_".
     @param enumclass : Class name that contains enums.
     @return : According enum value as integer.
     """
    for item in dir(enumclass):
        match = []
        for i, itempart in enumerate(item.split('_')):
            if itempart.isdigit():
                continue
            try:
                namepart = name.split('_')[i]
            except IndexError:
                continue
            match.append(__isabbreviation(namepart.upper(), itempart.upper()))
        if all(match):
            return getattr(enumclass, item)


def __isabbreviation(abbrev, item):
    """Return True if first char of 'abbrev' and 'item' match and all chars of 'abbrev' occur in 'item' in this order.
    @param abbrev : Case sensitive string.
    @param item : Case sensitive string.
    @return : True if 'abbrev' is an abbreviation of 'item'.
    """
    if not abbrev:
        return True
    if not item:
        return False
    if abbrev[0] != item[0]:
        return False
    return any(__isabbreviation(abbrev[1:], item[i + 1:]) for i in range(len(item)))


def getrecopt(name):
    """Return record option value according to 'name'.
    @param name: Short name of item, e.g. "CUR_POS". Case insensitive, separated by "_".
    @return : According enum value as integer.
    """
    return __getopt(name, RecordOptions)


def gettrigsources(name):
    """Return trigger option value according to 'name'.
    @param name: Short name of item, e.g. "CUR_POS". Case insensitive, separated by "_".
    @return : According enum value as integer.
    """
    return __getopt(name, TriggerSources)


def getservotime(gcs):
    """Return current servo cycle time in seconds as float.
    @type gcs : pipython.gcscommands.GCSCommands
    @return : Current servo cycle time in seconds as float.
    """
    servotime = None
    if gcs.devname in ['C-702.00']:
        servotime = SERVOTIMES[gcs.devname]
    if servotime is None:
        servotime = gcs.getparam(0x0E000200)  # SERVO_UPDATE_TIME
    if servotime is None:
        if gcs.devname in SERVOTIMES:
            servotime = SERVOTIMES[gcs.devname]
    if servotime is None:
        raise NotImplementedError('servo cycle time for %r is unknown' % gcs.devname)
    return float(servotime)


def getmaxnumvalues(gcs):  # 'getmaxnumvalues' is too complex (11) pylint: disable=C0901
    """Return maximum possible number of data recorder values as integer.
    @type gcs : pipython.gcscommands.GCSCommands
    @return : Maximum possible number of data recorder values as integer.
    """
    maxnumvalues = None
    if gcs.devname in ['C-702.00']:
        maxnumvalues = MAXNUMVALUES[gcs.devname]
    if not maxnumvalues:
        # E-517, E-518, E-852
        maxnumvalues = gcs.getparam(0x16000201)  # DATA REC SET POINTS
    if not maxnumvalues:
        # E-709, E-712, E-725, E-753.1CD, E-727, E-723K001
        maxpoints = gcs.getparam(0x16000200)  # DATA_REC_MAX_POINTS
        numtables = gcs.getparam(0x16000300)  # DATA_REC_CHAN_NUMBER
        if maxpoints and numtables:
            maxnumvalues = int(maxpoints / numtables)
    if not maxnumvalues:
        # C-843
        maxpoints = gcs.getparam(0x16000200)  # DATA_REC_MAX_POINTS
        if maxpoints:
            maxnumvalues = int(maxpoints / gcs.qTNR())
    if not maxnumvalues:
        # Mercury, etc.
        maxnumvalues = gcs.getparam(0x16000001)  # RECORDCYCLES_PER_TRIGGER
    if not maxnumvalues:
        if gcs.devname in MAXNUMVALUES:
            maxnumvalues = MAXNUMVALUES[gcs.devname]
    if not maxnumvalues:
        raise NotImplementedError('maximum number of data recorder values for %r is unknown' % gcs.devname)
    return maxnumvalues


class Datarecorder(FrozenClass):
    """Set up and use the data recorder of a PI device."""

    def __init__(self, gcs):
        """Set up and use the data recorder of a PI device connected via 'gcs'.
        @type gcs : pipython.gcscommands.GCSCommands
        """
        super(Datarecorder, self).__init__()
        debug('create an instance of Datarecorder(gcs=%s)', str(gcs))
        self.__gcs = gcs
        self.__cfg = {
            'servotime': None,
            'numvalues': None,
            'offset': None,
            'maxnumvalues': None,
            'samplerate': None,
            'sources': None,
            'options': None,
            'trigsources': None,
            'rectables': [],
        }
        self._freeze()

    @property
    def servotime(self):
        """Return current servo cycle time in seconds as float."""
        if self.__cfg['servotime'] is None:
            self.__cfg['servotime'] = getservotime(self.__gcs)
            debug('Datarecorder.servotime is %g secs', self.__cfg['servotime'])
        return self.__cfg['servotime']

    @servotime.setter
    def servotime(self, value):
        """Set current servo cycle time in seconds as float."""
        value = float(value)
        self.__cfg['servotime'] = value
        debug('Datarecorder.servotime set to %g secs', self.__cfg['servotime'])

    @property
    def numvalues(self):
        """Return number of data recorder values to record as integer."""
        if self.__cfg['numvalues'] is None:
            self.numvalues = self.maxnumvalues
        return self.__cfg['numvalues']

    @numvalues.setter
    def numvalues(self, value):
        """Set number of data recorder values to record to 'value' as integer."""
        value = int(value)
        if value > self.maxnumvalues:
            raise ValueError('%d exceeds the maximum number of data recorder values %d' % (value, self.maxnumvalues))
        self.__cfg['numvalues'] = value
        debug('Datarecorder.numvalues: set to %d', self.__cfg['numvalues'])

    @property
    def offset(self):
        """Return start point in the record table as integer, starts with index 1."""
        if self.__cfg['offset'] is None:
            if self.numvalues:
                return 1
        return self.__cfg['offset']

    @offset.setter
    def offset(self, value):
        """Set start point in the record table as integer, starts with index 1."""
        value = int(value)
        self.__cfg['offset'] = value
        debug('Datarecorder.offset: set to %d', self.__cfg['offset'])

    @property
    def maxnumvalues(self):
        """Return maximum possible number of data recorder values as integer."""
        if self.__cfg['maxnumvalues'] is None:
            self.__cfg['maxnumvalues'] = getmaxnumvalues(self.__gcs)
            debug('Datarecorder.maxnumvalues is %d', self.__cfg['maxnumvalues'])
        return self.__cfg['maxnumvalues']

    @maxnumvalues.setter
    def maxnumvalues(self, value):
        """Set maximum possible number of data recorder values as integer."""
        value = int(value)
        self.__cfg['maxnumvalues'] = value
        debug('Datarecorder.maxnumvalues: set to %d', self.__cfg['maxnumvalues'])

    @property
    def samplerate(self):
        """Return current sampling rate in multiples of servo cycle time as integer."""
        if self.__cfg['samplerate'] is None:
            if self.__gcs.HasqRTR():
                self.__cfg['samplerate'] = self.__gcs.qRTR()
            else:
                warning('device %r does not support the RTR? command', self.__gcs.devname)
                self.__cfg['samplerate'] = 1
        return self.__cfg['samplerate']

    @samplerate.setter
    def samplerate(self, value):
        """Set current sampling rate to 'value' in multiples of servo cycle time as integer."""
        value = max(1, int(value))
        if self.__gcs.HasRTR():
            self.__gcs.RTR(value)
            self.__cfg['samplerate'] = value
        else:
            warning('device %r does not support the RTR command', self.__gcs.devname)
            self.__cfg['samplerate'] = 1
        debug('Datarecorder.samplerate: set to %d servo cycles', self.__cfg['samplerate'])

    @property
    def sampletime(self):
        """Return current sampling time in seconds as float."""
        return self.samplerate * self.servotime

    @sampletime.setter
    def sampletime(self, value):
        """Set current sampling time to 'value' in seconds as float."""
        self.samplerate = int(float(value) / self.servotime)
        debug('Datarecorder.sampletime: set to %g s', self.sampletime)

    @property
    def samplefreq(self):
        """Return current sampling frequency in Hz as float."""
        return 1. / self.sampletime

    @samplefreq.setter
    def samplefreq(self, value):
        """Set current sampling frequency to 'value' in Hz as float."""
        self.sampletime = 1. / float(value)
        debug('Datarecorder.samplefreq: set to %.2f Hz', self.samplefreq)

    @property
    def rectime(self):
        """Return complete record time in seconds as float."""
        return self.numvalues * self.sampletime

    @rectime.setter
    def rectime(self, value):
        """Set number of values to record according to 'value' as complete record time in seconds as float."""
        self.numvalues = float(value) / self.sampletime
        debug('Datarecorder.frequency: set to %.2f Hz', self.samplefreq)

    @property
    def rectimemax(self):
        """Return complete record time in seconds as float."""
        return self.maxnumvalues * self.sampletime

    @rectimemax.setter
    def rectimemax(self, value):
        """Set sample time to record for 'value' seconds (float) with max. number of points."""
        self.numvalues = self.maxnumvalues
        self.sampletime = float(value) / self.numvalues
        debug('Datarecorder.rectimemax: %d values with sampling %g s', self.numvalues, self.sampletime)

    @property
    def sources(self):
        """Return current record source IDs as list of strings, defaults to first axis."""
        self.__cfg['sources'] = self.__cfg['sources'] or self.__gcs.axes[0]
        if isinstance(self.__cfg['sources'], (list, tuple)):
            return self.__cfg['sources']
        return [self.__cfg['sources']] * len(self.rectables)

    @sources.setter
    def sources(self, value):
        """Set record source IDs as string convertible or list of them."""
        self.__cfg['sources'] = value
        debug('Datarecorder.sources: set to %r', self.__cfg['sources'])

    @sources.deleter
    def sources(self):
        """Reset record source IDs."""
        self.__cfg['sources'] = None
        debug('Datarecorder.sources: reset')

    @property
    def options(self):
        """Return current record source IDs as list of integers, defaults to RecordOptions.ACTUAL_POSITION_2."""
        self.__cfg['options'] = self.__cfg['options'] or RecordOptions.ACTUAL_POSITION_2
        if isinstance(self.__cfg['options'], (list, tuple)):
            return self.__cfg['options']
        return [self.__cfg['options']] * len(self.rectables)

    @options.setter
    def options(self, value):
        """Set record source IDs as integer convertible or list of them."""
        self.__cfg['options'] = value
        debug('Datarecorder.options: set to %r', self.__cfg['options'])

    @options.deleter
    def options(self):
        """Reset record source IDs."""
        self.__cfg['options'] = None
        debug('Datarecorder.options: reset')

    @property
    def trigsources(self):
        """Return current trigger source as int or list, defaults to TriggerSources.NEXT_COMMAND_WITH_RESET_2."""
        self.__cfg['trigsources'] = self.__cfg['trigsources'] or TriggerSources.NEXT_COMMAND_WITH_RESET_2
        return self.__cfg['trigsources']

    @trigsources.setter
    def trigsources(self, value):
        """Set trigger source IDs. If single integer then "DRT 0" is used. If list
        of integers then list size can be 1 or must match the length of self.rectables.
        """
        if isinstance(value, tuple):
            value = list(value)
        self.__cfg['trigsources'] = value
        debug('Datarecorder.trigsources: set to %r', self.__cfg['trigsources'])

    @trigsources.deleter
    def trigsources(self):
        """Reset trigger source IDs."""
        self.__cfg['trigsources'] = None
        debug('Datarecorder.trigsources: reset')

    @property
    def rectables(self):
        """Return the record tables as list of integers."""
        if isinstance(self.__cfg['sources'], (list, tuple)):
            numtables = len(self.__cfg['sources'])
        elif isinstance(self.__cfg['options'], (list, tuple)):
            numtables = len(self.__cfg['options'])
        elif isinstance(self.__cfg['trigsources'], (list, tuple)):
            numtables = len(self.__cfg['trigsources'])
        else:
            numtables = 1
        self.__cfg['rectables'] = list(range(1, numtables + 1))
        return self.__cfg['rectables']

    def wait(self, timeout=0):
        """Wait for end of data recording.
        @param timeout : Timeout in seconds, is disabled by default.
        """
        if not self.rectables:
            raise SystemError('rectables are not set')
        numvalues = self.numvalues or self.maxnumvalues
        if self.__gcs.HasqDRL():
            maxtime = time() + timeout
            while min([self.__gcs.qDRL(table)[table] for table in self.rectables]) < numvalues:
                if timeout and time() > maxtime:
                    raise SystemError('timeout after %.1f secs while waiting on data recorder' % timeout)
        else:
            waittime = 1.2 * self.rectime
            debug('Datarecorder.wait: wait %.2f secs for data recording', waittime)
            sleep(waittime)

    def read(self, offset=None, numvalues=None, verbose=False):
        """Read out the data and return it.
        @param offset : Start point in the table as integer, starts with index 1, overwrites self.offset.
        @param numvalues : Number of points to be read per table as integer, overwrites self.numvalues.
        @param verbose : If True print a line that shows how many values have been read out already.
        @return : Tuple of (header, data), see qDRR command.
        """
        if not self.rectables:
            raise SystemError('rectables are not set')
        header = self.__gcs.qDRR(self.rectables, offset or self.offset, numvalues or self.numvalues)
        while self.__gcs.bufstate is not True:
            if verbose:
                print(('\rread data {:.1f}%...'.format(self.__gcs.bufstate * 100)), end='')
                sleep(0.05)
        if verbose:
            print(('\r%s\r' % (' ' * 20)), end='')
        data = self.__gcs.bufdata
        return header, data

    def getdata(self, timeout=0, offset=None, numvalues=None):
        """Wait for end of data recording, start reading out the data and return the data.
        @param timeout : Timeout in seconds, is disabled by default.
        @param offset : Start point in the table as integer, starts with index 1, overwrites self.offset.
        @param numvalues : Number of points to be read per table as integer, overwrites self.numvalues.
        @return : Tuple of (header, data), see qDRR command.
        """
        self.wait(timeout)
        return self.read(offset, numvalues)

    def arm(self):
        """Ready the data recorder with given options and activate the trigger.
        If TriggerSources.NEXT_COMMAND_WITH_RESET_2 is used then the error check will be disabled.
        """
        if self.__gcs.HasDRC():
            for i in range(len(self.rectables)):
                self.__gcs.DRC(self.rectables[i], self.sources[i], self.options[i])
        else:
            warning('device %r does not support the DRC command', self.__gcs.devname)
        if self.__gcs.HasDRT():
            errcheck = None
            if isinstance(self.trigsources, (list, tuple)):
                if TriggerSources.NEXT_COMMAND_WITH_RESET_2 in self.trigsources:
                    errcheck = self.__gcs.errcheck
                    self.__gcs.errcheck = False
                if len(self.trigsources) == 1:
                    self.trigsources = [self.trigsources[0]] * len(self.rectables)
                for i in range(len(self.rectables)):
                    self.__gcs.DRT(self.rectables[i], self.trigsources[i])
            else:
                if TriggerSources.NEXT_COMMAND_WITH_RESET_2 == self.trigsources:
                    errcheck = self.__gcs.errcheck
                    self.__gcs.errcheck = False
                self.__gcs.DRT(0, self.trigsources)
            if errcheck is not None:
                self.__gcs.errcheck = errcheck
        else:
            warning('device %r does not support the DRT command', self.__gcs.devname)

    @property
    def timescale(self):
        """Return list of values for time scale of recorded data."""
        return [1. / self.samplerate * x for x in range(self.numvalues)]
