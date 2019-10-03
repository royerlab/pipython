#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Wrapper to access a PI GCS DLL."""

import ctypes
from logging import debug, warning
import os
from platform import architecture
import sys

from pipython.gcserror import GCSError
from pipython.interfaces.pigateway import PIGateway

__signature__ = 0x55cb39e7dd6eea53d3bd96f99c1c60cf

DLLDEVICES = {
    'PI_GCS2_DLL': ['C-413', 'C-663', 'C-863', 'C-867', 'C-877', 'C-884', 'C-885', 'C-887',
                    'C-891', 'E-517', 'E-518', 'E-545', 'E-709', 'E-712', 'E-723', 'E-725',
                    'E-727', 'E-753', 'E-754', 'E-755', 'E-852B0076', 'E-861', 'E-870', 'E-871',
                    'E-873', ],
    'C7XX_GCS_DLL': ['C-702', ],
    'C843_GCS_DLL': ['C-843', ],
    'C848_DLL': ['C-848', ],
    'C880_DLL': ['C-880', ],
    'E816_DLL': ['E-621', 'E-625', 'E-665', 'E-816', 'E816', ],
    'E516_DLL': ['E-516', ],
    'PI_Mercury_GCS_DLL': ['C-663.10', 'C-863.10', 'MERCURY', 'MERCURY_GCS1', ],
    'PI_HydraPollux_GCS2_DLL': ['HYDRA', 'POLLUX', 'POLLUX2', 'POLLUXNT', ],
    'E7XX_GCS_DLL': ['DIGITAL PIEZO CONTROLLER', 'E-710', 'E-761', ],
    'HEX_GCS_DLL': ['HEXAPOD', 'HEXAPOD_GCS1', ],
    'PI_G_GCS2_DLL': ['UNKNOWN', ],
}

UNIXDLL = {
    'E7XX_GCS_DLL': 'libpi_e7xx_gcs',
    'PI_HydraPollux_GCS2_DLL': 'libpi_hydrapollux',
    'PI_GCS2_DLL': 'libpi_pi_gcs2',
}


def get_dll_name(devname):
    """Get according name of 32 or 64 bit PI GCS DLL for 'devname'.
    @param devname : Name of device as upper or lower case string.
    @return : Name of DLL as string.
    """
    if not devname:
        dllname = 'PI_GCS2_DLL'
    elif devname.upper() in ('C-663.10', 'C-863.10'):
        dllname = 'PI_Mercury_GCS_DLL'
    else:
        devname = devname.split('.')[0]
        devname = devname.split('K')[0]
        dllname = ''
        for dll in DLLDEVICES:
            for device in DLLDEVICES[dll]:
                if devname.upper() == device.upper():
                    dllname = dll
                    break
    if not dllname:
        raise NotImplementedError('unknown device name %r' % devname)
    return modify_dll_name(dllname)


def modify_dll_name(dllname):
    """Modify windows 'dllname' for Linux/Mac systems and according architecture.
    @param dllname : File name of Windows dll.
    @return : Name of DLL as string according to operating system and architecture.
    """
    if sys.platform in ('linux', 'linux2', 'darwin'):
        unixdll = UNIXDLL.get(dllname)
        if unixdll is None:
            raise NotImplementedError('%r is not available for this operating system' % dllname)
        if sys.platform in ('darwin',):
            unixdll += '.dylib'
        else:
            unixdll += '.so'
        return unixdll
    if architecture()[0] == '32bit':
        dllname += '.dll'
    else:
        dllname += '_x64.dll'
    return dllname


def get_dll_path(dllname):
    """Return absolute path to GCS DLL as string.
    Search for GCS DLL in this order: 'dllname' is absolute path to GCS DLL. If not, return
    GCSTranslator path from registry/sysenv. If not set return current working directory.
    @param dllname : Name or path to GCS DLL.
    @return : Absolute path to GCS DLL as string.
    """
    if os.path.dirname(dllname):
        if os.path.isfile(dllname):
            return os.path.normpath(os.path.abspath(dllname))
    gcsdir = get_gcstranslator_dir()
    return os.path.normpath(os.path.abspath(os.path.join(gcsdir, dllname)))


def get_gcstranslator_dir():
    """Return GCSTranslator directory from Windows registry, from defined UNIX path, or
    if directory does not exist, return current working directory.
    @return : GCSTranslator directory as string.
    """
    gcsdir = os.getcwd()
    if sys.platform in ('win32', 'cygwin'):
        gcsdir = read_registry_gcstranslator(gcsdir)
    elif sys.platform in ('linux', 'linux2', 'darwin'):
        if architecture()[0] == '32bit':
            if os.path.isdir('/usr/local/PI/lib32'):
                gcsdir = '/usr/local/PI/lib32'
        else:
            if os.path.isdir('/usr/local/PI/lib64'):
                gcsdir = '/usr/local/PI/lib64'
    else:
        raise NotImplementedError('unsupported operating system %r' % sys.platform)
    return gcsdir


def read_registry_gcstranslator(gcsdir):
    """Return GCSTranslator directory from Windows registry.
    @param gcsdir : Default GCSTranslator directory.
    @return : GCSTranslator directory as string from registry or 'gcsdir' if reading registry fails.
    """
    try:
        import winreg  # Python 3
    except ImportError:
        import _winreg as winreg  # Python 2
    if 'PROCESSOR_ARCHITEW6432' in os.environ:
        regkey = r'SOFTWARE\Wow6432Node\PI\GCSTranslator'
    else:
        regkey = r'SOFTWARE\PI\GCSTranslator'
    reghandle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    try:
        keyhandle = winreg.OpenKey(reghandle, regkey)
        gcsdir = winreg.QueryValueEx(keyhandle, 'Path')[0]
        winreg.CloseKey(keyhandle)
    except WindowsError:
        warning('no GCSTranslator path in Windows registry (HKLM\\%s)', regkey)
    else:
        debug('read HKLM\\%s: %r', regkey, gcsdir)
    finally:
        winreg.CloseKey(reghandle)
    return gcsdir


# Invalid method name pylint: disable=C0103
# Too many public methods pylint: disable=R0904
# Too many instance attributes pylint: disable=R0902
class GCSDll(PIGateway):
    """Wrapper to access a PI GCS DLL."""

    def __init__(self, devname='', dllname=''):
        """Wrapper to access a PI GCS DLL.
        @param devname : Name of device, chooses according DLL which defaults to PI_GCS2_DLL.
        @param dllname : Name or path to GCS DLL to use, overwrites 'devname'.
        """
        debug('create an instance of GCSDll(devname=%r, dllname=%r)', devname, dllname)
        dllname = dllname or get_dll_name(devname)
        self.__dllpath = get_dll_path(dllname)
        self.__dllprefix = None
        self.__dllhandle = None
        self.__id = -1
        self.__dcid = -1
        self.__ifdescription = ''
        self.__asyncbufferindex = -1  # DEPRECATED
        self.__warnmsg = ''

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unload()

    def __str__(self):
        return 'GCSDll(%s)' % self.__dllpath

    @property
    def warning(self):
        """Get the current warning as string and reset the warning."""
        warnmsg = self.__warnmsg
        self.__warnmsg = ''
        return warnmsg

    def send(self, msg):
        """Send a GCS command to the device, do not query error from device.
        @param msg : GCS command as string, with or without trailing line feed character.
        """
        debug('GCSDll.send(id%d): %r', self.__id, msg)
        msg = ctypes.c_char_p(str(msg).encode())
        if not getattr(self.__handle, self.__prefix + 'GcsCommandset')(self.__id, msg):
            raise GCSError(self.__error)

    @property
    def answersize(self):
        """Get the size of an answer of a GCS command as integer."""
        size = ctypes.c_int()
        if not getattr(self.__handle, self.__prefix + 'GcsGetAnswerSize')(self.__id, ctypes.byref(size)):
            raise GCSError(self.__error)
        return size.value

    def getanswer(self, bufsize):
        """Get the answer of a GCS command.
        @param bufsize : Size in characters of string buffer to store the answer as integer.
        @return : Answer as string.
        """
        bufstr = ctypes.create_string_buffer('\000'.encode(), bufsize + 2)
        if not getattr(self.__handle, self.__prefix + 'GcsGetAnswer')(self.__id, bufstr, bufsize + 1):
            raise GCSError(self.__error)
        try:
            answer = bufstr.value.decode(encoding='cp1252')
        except UnicodeDecodeError:
            answer = bufstr.value
        debug('GCSDll.getanswer(id%d): %r', self.__id, answer)
        return answer

    def close(self):
        """Close connection to device and daisy chain."""
        if self.__id >= 0:
            self.CloseConnection()
        if self.__dcid >= 0:
            self.CloseDaisyChain()

    def unload(self):
        """Close connection to device and daisy chain and unload GCS DLL."""
        if self.__dllhandle is None:
            warning('GCSDll.unload: cannot unload %r', self.__dllpath)
        else:
            self.close()
            # Access to a protected member _handle of a client class pylint: disable=W0212
            if sys.platform in ('win32', 'cygwin'):
                ctypes.windll.kernel32.FreeLibrary(ctypes.c_int(self.__dllhandle._handle))
            else:
                ctypes.cdll.LoadLibrary(self.__dllpath).dlclose(ctypes.c_int(self.__dllhandle._handle))
            self.__dllhandle = None
            debug('GCSDll.unload %r', self.__dllpath)

    @property
    def __error(self):
        """Get error status of the DLL as integer."""
        return getattr(self.__handle, self.__prefix + 'GetError')(self.__id)

    @property
    def __handle(self):
        """Return handle to GCS DLL, optionally load GCS DLL."""
        if self.__dllhandle is None:
            if not os.path.isfile(self.__dllpath):
                raise IOError('%r not found' % self.__dllpath)
            debug('GCSDll.load: %r', self.__dllpath)
            if sys.platform in ('win32', 'cygwin'):
                self.__dllhandle = ctypes.windll.LoadLibrary(self.__dllpath)
            else:
                self.__dllhandle = ctypes.cdll.LoadLibrary(self.__dllpath)
        return self.__dllhandle

    @property
    def __prefix(self):
        """Return function prefix according to the name of the GCS DLL as string."""
        if self.__dllprefix is None:
            dllname = os.path.splitext(os.path.basename(self.__dllpath))[0]
            for winname in UNIXDLL:
                if dllname == UNIXDLL[winname]:
                    dllname = winname
                    break
            if dllname.find('PI_MERCURY_GCS_DLL') > -1:
                self.__dllprefix = 'Mercury_'
            elif dllname.find('PI_HydraPollux_GCS2_DLL') > -1:
                self.__dllprefix = 'Hydra_'
            elif dllname.find('PI_G_GCS2_DLL') > -1:
                self.__dllprefix = 'PI_G_'
            else:
                self.__dllprefix = '%s_' % dllname.split('_')[0]
        return self.__dllprefix

    @property
    def connectionid(self):
        """Get ID of current connection as integer."""
        return self.__id

    @property
    def dcid(self):
        """Get ID of current daisy chain connection as integer."""
        return self.__dcid

    @property
    def dllpath(self):
        """Get full path to GCS DLL."""
        return self.__dllpath

    def GetAsyncBuffer(self, firstline=1, lastline=0, numtables=1):
        """Query all available data points, return list with 'numtables' columns.
        DEPRECATED: Use GCSMessages.bufdata instead.
        Buffer is used by qDRR(), qDDL(), qGWD(), qTWS(), qJLT() and qHIT().
        @param firstline : Optional, but must be >= 1 and smaller than 'lastline'.
        @param lastline : Optional, defaults to query all available data points.
        @param numtables : Arrange data into 'numtables' columns, defaults to "1".
        @return: List of data points as float with 'numtables' columns.
        """
        debug('DEPRECATED -- GcsDll.GetAsyncBuffer(id%d, firstline=%r, lastline=%r, numtables=%r)', self.__id,
              firstline, lastline, numtables)
        maxindex = lastline * numtables or self.__asyncbufferindex
        if firstline < 1:
            raise SystemError('firstline must be 1 or larger')
        minindex = (firstline - 1) * numtables
        if minindex > maxindex:
            raise SystemError('firstline must not be larger than lastline')
        cvalues = ctypes.byref(ctypes.c_float)
        if not getattr(self.__handle, self.__prefix + 'GetAsyncBuffer')(self.__id, cvalues):
            raise GCSError(self.__error)
        data = [[] for _ in range(numtables)]
        for i in range(minindex, maxindex):
            data[i % numtables].append(float(cvalues[i]))
        debug('DEPRECATED -- GCSDll.GetAsyncBuffer(id%d): %r', self.__id, data)
        return data

    def GetAsyncBufferIndex(self):
        """Get current index used for the internal buffer.
        DEPRECATED: Use GCSMessages.bufindex instead.
        @return: Buffer index as integer.
        """
        bufindex = getattr(self.__handle, self.__prefix + 'GetAsyncBufferIndex')(self.__id)
        debug('DEPRECATED -- GCSDll.GetAsyncBufferIndex(id%d): %r', self.__id, bufindex)
        self.__asyncbufferindex = bufindex
        return bufindex

    def IsConnected(self):
        """Return True if a device is connected."""
        return bool(getattr(self.__handle, self.__prefix + 'IsConnected')(self.__id))

    def GetInterfaceDescription(self):
        """Get textual description of actual interface connection."""
        return self.__ifdescription

    def InterfaceSetupDlg(self, key=''):
        """Open dialog to select the interface.
        @param key: Optional key name as string to store the settings in the Windows registry.
        """
        debug('GCSDll.InterfaceSetupDlg(key=%r)', key)
        key = ctypes.c_char_p(str(key).encode())
        self.__id = getattr(self.__handle, self.__prefix + 'InterfaceSetupDlg')(key)
        if self.__id < 0:
            raise GCSError(self.__error)
        self.__ifdescription = 'Interface Setup Dialog'

    def ConnectRS232(self, comport, baudrate):
        """Open an RS-232 connection to the device.
        @param comport: Port to use as integer (1 means "COM1") or name ("dev/ttys0") as string.
        @param baudrate: Baudrate to use as integer.
        """
        cbaudrate = ctypes.c_int(baudrate)
        try:
            comport = int(comport)
        except ValueError:
            debug('GCSDll.ConnectRS232ByDevName(devname=%r, baudrate=%s)', comport, baudrate)
            cdevname = ctypes.c_char_p(str(comport).encode())
            self.__id = getattr(self.__handle, self.__prefix + 'ConnectRS232ByDevName')(cdevname, cbaudrate)
        else:
            debug('GCSDll.ConnectRS232(comport=%s, baudrate=%s)', comport, baudrate)
            ccomport = ctypes.c_int(comport)
            self.__id = getattr(self.__handle, self.__prefix + 'ConnectRS232')(ccomport, cbaudrate)
        if self.__id < 0:
            raise GCSError(self.__error)
        self.__ifdescription = 'RS-232 port %s, %s Baud' % (comport, baudrate)

    def ConnectTCPIP(self, ipaddress, ipport=50000):
        """Open a TCP/IP connection to the device.
        @param ipaddress: IP address to connect to as string.
        @param ipport: Port to use as integer, defaults to 50000.
        """
        debug('GCSDll.ConnectTCPIP(ipaddress=%s, ipport=%s)', ipaddress, ipport)
        cipaddress = ctypes.c_char_p(str(ipaddress).encode())
        cipport = ctypes.c_int(ipport)
        self.__id = getattr(self.__handle, self.__prefix + 'ConnectTCPIP')(cipaddress, cipport)
        if self.__id < 0:
            raise GCSError(self.__error)
        self.__ifdescription = 'TCPIP %s:%s' % (ipaddress, ipport)

    def ConnectTCPIPByDescription(self, description):
        """Open a TCP/IP connection to the device using the device 'description'.
        @param description: One of the identification strings listed by EnumerateTCPIPDevices().
        """
        debug('GCSDll.ConnectTCPIPByDescription(description=%r)', description)
        cdescription = ctypes.c_char_p(str(description).encode())
        self.__id = getattr(self.__handle, self.__prefix + 'ConnectTCPIPByDescription')(cdescription)
        if self.__id < 0:
            raise GCSError(self.__error)
        self.__ifdescription = 'TCPIP %r' % description

    def ConnectUSB(self, serialnum):
        """Open an USB connection to a device.
        @param serialnum: Serial number of device or one of the
        identification strings listed by EnumerateUSB().
        """
        debug('GCSDll.ConnectUSB(serialnum=%r)', serialnum)
        cserialnum = ctypes.c_char_p(str(serialnum).encode())
        self.__id = getattr(self.__handle, self.__prefix + 'ConnectUSB')(cserialnum)
        if self.__id < 0:
            raise GCSError(self.__error)
        self.__ifdescription = 'USB %r' % serialnum

    def ConnectNIgpib(self, board, device):
        """Open a connection from a NI IEEE 488 board to the device.
        @param board: GPIB board ID as integer.
        @param device: The GPIB device ID of the device as integer.
        """
        debug('GCSDll.ConnectNIgpib(board=%s, device=%s)', board, device)
        cboard = ctypes.c_int(board)
        cdevice = ctypes.c_int(device)
        self.__id = getattr(self.__handle, self.__prefix + 'ConnectNIgpib')(cboard, cdevice)
        if self.__id < 0:
            raise GCSError(self.__error)
        self.__ifdescription = 'GPIB board %s, device %s' % (board, device)

    def ConnectPciBoard(self, board):
        """Open a PCI board connection.
        @param board : PCI board number as integer.
        """
        debug('GCSDll.ConnectPciBoard(board=%s)', board)
        cboard = ctypes.c_int(board)
        if self.__prefix == 'C843_':
            self.__id = getattr(self.__handle, self.__prefix + 'Connect')(cboard)
        else:
            self.__id = getattr(self.__handle, self.__prefix + 'ConnectPciBoard')(cboard)
        if self.__id < 0:
            raise GCSError(self.__error)
        self.__ifdescription = 'PCI board %s' % board

    def EnumerateUSB(self, mask=''):
        """Get identification strings of all USB connected devices.
        @param mask: String to filter the results for certain text.
        @return: Found devices as list of strings.
        """
        debug('GCSDll.EnumerateUSB(mask=%r)', mask)
        mask = ctypes.c_char_p(str(mask).encode())
        bufsize = 100000
        bufstr = ctypes.create_string_buffer('\000'.encode(), bufsize + 2)
        if getattr(self.__handle, self.__prefix + 'EnumerateUSB')(bufstr, bufsize, mask) < 0:
            raise GCSError(self.__error)
        devlist = bufstr.value.decode().split('\n')[:-1]
        devlist = [item.strip() for item in devlist]
        debug('GCSDll.EnumerateUSB: %r', devlist)
        return devlist

    def EnumerateTCPIPDevices(self, mask=''):
        """Get identification strings of all TCP connected devices.
        @param mask: String to filter the results for certain text.
        @return: Found devices as list of strings.
        """
        debug('GCSDll.EnumerateTCPIPDevices(mask=%r)', mask)
        mask = ctypes.c_char_p(str(mask).encode())
        bufsize = 100000
        bufstr = ctypes.create_string_buffer('\000'.encode(), bufsize + 2)
        if getattr(self.__handle, self.__prefix + 'EnumerateTCPIPDevices')(bufstr, bufsize, mask) < 0:
            raise GCSError(self.__error)
        devlist = bufstr.value.decode().split('\n')[:-1]
        devlist = [item.strip() for item in devlist]
        debug('GCSDll.EnumerateTCPIPDevices: %r', devlist)
        return devlist

    def OpenRS232DaisyChain(self, comport, baudrate):
        """Open an RS-232 daisy chain connection.
        To get access to a daisy chain device you have to call ConnectDaisyChainDevice().
        @param comport: Port to use as integer (1 means "COM1").
        @param baudrate: Baudrate to use as integer.
        @return: Found devices as list of strings.
        """
        debug('GCSDll.OpenRS232DaisyChain(comport=%s, baudrate=%s)', comport, baudrate)
        ccomport = ctypes.c_int(comport)
        cbaudrate = ctypes.c_int(baudrate)
        numdev = ctypes.byref(ctypes.c_int())
        bufsize = 10000
        bufstr = ctypes.create_string_buffer('\000'.encode(), bufsize + 2)
        self.__dcid = getattr(self.__handle, self.__prefix + 'OpenRS232DaisyChain')(ccomport, cbaudrate, numdev, bufstr,
                                                                                    bufsize)
        if self.__dcid < 0:
            raise GCSError(self.__error)
        devlist = bufstr.value.decode().split('\n')[:-1]
        devlist = [item.strip() for item in devlist]
        debug('GCSDll.OpenRS232DaisyChain: %r', devlist)
        self.__ifdescription = 'RS-232 daisy chain at COM%s, %s Baud' % (comport, baudrate)
        return devlist

    def OpenUSBDaisyChain(self, description):
        """Open a USB daisy chain connection.
        To get access to a daisy chain device you have to call ConnectDaisyChainDevice().
        @param description: Description of the device returned by EnumerateUSB().
        @return: Found devices as list of strings.
        """
        debug('GCSDll.OpenUSBDaisyChain(description=%r)', description)
        cdescription = ctypes.c_char_p(str(description).encode())
        numdev = ctypes.byref(ctypes.c_int())
        bufsize = 10000
        bufstr = ctypes.create_string_buffer('\000'.encode(), bufsize + 2)
        self.__dcid = getattr(self.__handle, self.__prefix + 'OpenUSBDaisyChain')(cdescription, numdev, bufstr, bufsize)
        if self.__dcid < 0:
            raise GCSError(self.__error)
        devlist = bufstr.value.decode().split('\n')[:-1]
        devlist = [item.strip() for item in devlist]
        debug('GCSDll.OpenUSBDaisyChain: %r', devlist)
        self.__ifdescription = 'USB daisy chain at SN %r' % description
        return devlist

    def OpenTCPIPDaisyChain(self, ipaddress, ipport=50000):
        """Open a TCPIP daisy chain connection.
        To get access to a daisy chain device you have to call ConnectDaisyChainDevice().
        @param ipaddress: IP address to connect to as string.
        @param ipport: Port to use as integer, defaults to 50000.
        @return: Found devices as list of strings.
        """
        debug('GCSDll.OpenTCPIPDaisyChain(ipaddress=%r, ipport=%s)', ipaddress, ipport)
        cipaddress = ctypes.c_char_p(str(ipaddress).encode())
        cipport = ctypes.c_int(ipport)
        numdev = ctypes.byref(ctypes.c_int())
        bufsize = 10000
        bufstr = ctypes.create_string_buffer('\000'.encode(), bufsize + 2)
        self.__dcid = getattr(self.__handle, self.__prefix + 'OpenTCPIPDaisyChain')(cipaddress, cipport, numdev, bufstr,
                                                                                    bufsize)
        if self.__dcid < 0:
            raise GCSError(self.__error)
        devlist = bufstr.value.decode().split('\n')[:-1]
        devlist = [item.strip() for item in devlist]
        debug('GCSDll.OpenTCPIPDaisyChain: %r', devlist)
        self.__ifdescription = 'TCPIP daisy chain at %s:%s' % (ipaddress, ipport)
        return devlist

    def ConnectDaisyChainDevice(self, deviceid, daisychainid=None):
        """Connect device with 'deviceid' on the daisy chain 'daisychainid'.
        Daisy chain has to be connected before, see Open<interface>DaisyChain() functions.
        @param daisychainid : Daisy chain ID as int from the daisy chain master instance or None.
        @param deviceid : Device ID on the daisy chain as integer.
        """
        debug('GCSDll.ConnectDaisyChainDevice(deviceid=%s, daisychainid=%s)', deviceid,
              daisychainid)
        if daisychainid is None:
            daisychainid = self.__dcid
        cdeviceid = ctypes.c_int(deviceid)
        cdaisychainid = ctypes.c_int(daisychainid)
        self.__id = getattr(self.__handle, self.__prefix + 'ConnectDaisyChainDevice')(cdaisychainid, cdeviceid)
        if self.__id < 0:
            raise GCSError(self.__error)
        if self.__ifdescription:
            self.__ifdescription += '; '
        self.__ifdescription += 'daisy chain %d, device %s' % (daisychainid, deviceid)

    def CloseConnection(self):
        """Close connection to the device."""
        debug('GCSDll.CloseConnection(id=%d)', self.__id)
        getattr(self.__handle, self.__prefix + 'CloseConnection')(self.__id)
        self.__ifdescription = self.__ifdescription.split(';')[0]
        self.__id = -1

    def CloseDaisyChain(self):
        """Close all connections on daisy chain and daisy chain connection itself."""
        debug('GCSDll.CloseDaisyChain(dcid=%d)', self.__dcid)
        getattr(self.__handle, self.__prefix + 'CloseDaisyChain')(self.__dcid)
        self.__ifdescription = ''
        self.__id = -1
        self.__dcid = -1

    def AddStage(self, axis):
        """Add a dataset for a user defined stage to the PI stages database.
        @param axis: Name of axis whose stage parameters should be added as string.
        """
        debug('GCSDll.AddStage(axis=%r)', axis)
        axis = ctypes.c_char_p(str(axis).encode())
        if not getattr(self.__handle, self.__prefix + 'AddStage')(self.__id, axis):
            raise GCSError(self.__error)

    def RemoveStage(self, axis):
        """Remove a dataset of a user defined stage from the PI stages database.
        @param axis: Name of axis whose stage parameters should be removed as string.
        """
        debug('GCSDll.RemoveStage(axis=%r)', axis)
        axis = ctypes.c_char_p(str(axis).encode())
        if not getattr(self.__handle, self.__prefix + 'RemoveStage')(self.__id, axis):
            raise GCSError(self.__error)

    def applyconfig(self, items, config):
        """Write parameters according to 'config' from PIStages database to controller.
        @param items : Items of the controller the configuration is assigned to as string.
        Consists of the key word (e.g. "axis") and ID  (e.g. "4"), examples: "axis 1", "axis 4".
        @param config: Name of a configuration existing in PIStages database as string.
        """
        debug('GCSDll.applyconfig(items=%r, config=%r)', items, config)
        items = ctypes.c_char_p(str(items).encode())
        config = ctypes.c_char_p(str(config).encode())
        bufsize = 20000
        warnings = ctypes.create_string_buffer('\000'.encode(), bufsize + 2)
        funcname = self.__prefix + 'WriteConfigurationFromDatabaseToController'
        if not getattr(self.__handle, funcname)(self.__id, items, config, warnings, bufsize + 1):
            self.__warnmsg = warnings.value.decode(encoding='cp1252')
            raise GCSError(self.__error)

    def saveconfig(self, items, config):
        """Read parameters according to 'config' from controller and write them to the PIStages database.
        @param items : Items of the controller the configuration is assigned to as string.
        Consists of the key word (e.g. "axis") and ID  (e.g. "4"), examples: "axis 1", "axis 4".
        @param config: Name of a configuration not yet existing in PIStages database as string.
        """
        debug('GCSDll.saveconfig(items=%r, config=%r)', items, config)
        items = ctypes.c_char_p(str(items).encode())
        config = ctypes.c_char_p(str(config).encode())
        bufsize = 20000
        warnings = ctypes.create_string_buffer('\000'.encode(), bufsize + 2)
        funcname = self.__prefix + 'ReadConfigurationFromControllerToDatabase'
        if not getattr(self.__handle, funcname)(self.__id, items, config, warnings, bufsize + 1):
            self.__warnmsg = warnings.value.decode(encoding='cp1252')
            raise GCSError(self.__error)

    def getconfigs(self):
        """Get available configurations in PIStages database for the connected controller.
        @return : Answer as string.
        """
        debug('GCSDll.getconfigs()')
        bufsize = 20000
        configs = ctypes.create_string_buffer('\000'.encode(), bufsize + 2)
        funcname = self.__prefix + 'GetAvailableControllerConfigurationsFromDatabase'
        if not getattr(self.__handle, funcname)(self.__id, configs, bufsize + 1):
            raise GCSError(self.__error)
        configs = configs.value.decode(encoding='cp1252')
        debug('GCSDll.getconfigs(id%d): %r', self.__id, configs)
        return configs
