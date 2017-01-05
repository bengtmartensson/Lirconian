#! /usr/bin/python3

# Copyright (C) 2017 Bengt Martensson.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see http://www.gnu.org/licenses/.

"""
This is a new and independent implementation of the Lirc irsend(1) program. It offers
a Python API and a command line interface. The command line interface is almost,
but not quite, compatible with irsend. Instead, it is organized as a program
with subcommands, send_once, etc.

There are some other subtile differences from irsend:

* subcommand must be lower case,
* send_once only takes one command (irsend takes several),
* send_stop without arguments uses the remote and the command from the last send_start command,
* no need to give dummy empty arguments for list,
* The --count argument to send_once is argument to the subcommand.
* the code in list remote is suppressed, unless -c is given,
* port number must be given with the --port (-p) argument; hostip:portnumber is not recognized,
* verbose option --verbose (-v)
* selectable timeout with --timeout (-t) option
* better error messages

The subcommands set_input_log, set_driver_options, and simulate are presently not
implemented. (The first two are not documented for irsend anyhow...).
Help is welcome.

It does not depend on anything but standard Python libraries.

For a GUI version, look at IrScrutinizer.
For a Java version, look at JavaLircClient https://github.com/bengtmartensson/JavaLircClient
"""

import argparse
import socket
import sys
import re
import os

VERSION = "LircClient 0.1.0"
READCHUNK = 4096
LINEFEED = 10
DEFAULT_LIRC_DEVICE = '/var/run/lirc/lircd'
DEFAULT_PORT = 8765

class LircServerException(Exception):
    pass


class BadPacketException(Exception):
    pass


class ThisCannotHappenException(Exception):
    pass


class AbstractLircClient:
    """
    Abstract base class for the LircClient. To implement, needs to assign the abstract "socket" to something.
    """
    P_BEGIN = 0
    P_MESSAGE = 1
    P_STATUS = 2
    P_DATA = 3
    P_N = 4
    P_DATA_N = 5
    P_END = 6
    P_DONE = 7

    _socket = None
    _verbose = False
    _timeout = None

    _lastRemote = None
    _lastCommand = None
    _socket = None
    _inBuffer = None

    def __init__(self, verbose, timeout):
        self._verbose = verbose
        self._timeout = timeout

    def setVerbosity(self, verbosity):
        self._verbose = verbosity

    def close(self):
        self._socket.close()

    def setTimeout(self, timeout):
        _timeout = timeout

    def readLine(self):
        if self._inBuffer is None or len(self._inBuffer) == 0:
            self._inBuffer = self._socket.recv(READCHUNK)

        while LINEFEED not in self._inBuffer:
            self._inBuffer += self._socket.recv(READCHUNK)

        n = self._inBuffer.find(LINEFEED);
        if n == -1:
            return None
        line = self._inBuffer[0:n].decode("US-ASCII")
        self._inBuffer = self._inBuffer[n+1:len(self._inBuffer)]
        return line

    def sendString(self, cmd):
        self._socket.send(bytearray(cmd, 'US-ASCII'))

    def sendCommand(self, packet):
        if self._verbose:
            print("Sending command `" + packet + "' to Lirc@" + self._socket.__str__())

        self.sendString(packet + '\n')

        result = []
        success = True

        state = self.P_BEGIN
        linesReceived = 0
        linesExpected = -1

        while state != self.P_DONE:
            string = self.readLine()
            if self._verbose:
                print('Received "{0}"'.format((string if string is not None else '')))

            if string == None:
                state = self.P_DONE
                continue

            if state == self.P_BEGIN:
                if string == "BEGIN":
                    state = self.P_MESSAGE
            elif state == self.P_MESSAGE:
                state = self.P_STATUS if string.strip().lower() == packet.lower() else self.P_BEGIN
            elif state == self.P_STATUS:
                if string == "SUCCESS":
                    state = self.P_DATA
                elif string == "END":
                    state = self.P_DONE
                elif string == "ERROR":
                    state = self.P_DATA
                    success = False
                else:
                    raise BadPacketException()
            elif state == self.P_DATA:
                if string == "END":
                    state = self.P_DONE
                elif string == "DATA":
                     state = self.P_N
                else:
                    raise BadPacketException()
            elif state == self.P_N:
                linesExpected = int(string)
                state = self.P_END if linesExpected == 0 else self.P_DATA_N
            elif state == self.P_DATA_N:
                result.append(string)
                linesReceived += 1
                if linesReceived == linesExpected:
                    state = self.P_END
            elif state == self.P_END:
                if string == "END":
                    state = self.P_DONE
                else:
                    raise BadPacketException()
            else:
                raise ThisCannotHappenException("Unhandled case (programming error)")

        if self._verbose:
            print("Lirc command " + ("succeded." if success else "failed."))

        if not success:
            raise LircServerException(''.join(result))

        return result

    def sendIrCommand(self, remote, command, count):
        _lastRemote = remote
        _lastCommand = command
        return self.sendCommand("SEND_ONCE " + remote + " " + command + " " + str(count)) is not None

    def sendIrCommandRepeat(self, remote, command):
        _lastRemote = remote
        _lastCommand = command
        return self.sendCommand("SEND_START " + remote + " " + command) is not None

    def stopIr(self, remote = None, command = None):
        return self.sendCommand("SEND_STOP " + (remote if remote is not None else self._lastRemote) + " " + (command if command is not None else self._lastCommand)) is not None

    def getRemotes(self):
        return self.sendCommand("LIST")

    def getCommands(self, remote, includeCodes = False):
        raw = self.sendCommand("LIST " + remote)
        if includeCodes:
            return raw
        result = []
        for cmd in raw:
            result.append(re.sub(r'^[0-9a-fA-F]* +', '', cmd))
        return result

    def setTransmitters(self, transmitters):
        mask = 0
        for transmitter in transmitters:
            mask |= (1 << (int(transmitter) - 1))
        return self.setTransmittersMask(mask) is not None

    def setTransmittersMask(self, mask):
        s = "SET_TRANSMITTERS " + str(mask)
        return self.sendCommand(s) is not None

    def getVersion(self):
        result = self.sendCommand("VERSION")
        version = result[0]
        return version


class UnixDomainSocketLircClient(AbstractLircClient):

    def __init__(self, socketAddress = DEFAULT_LIRC_DEVICE, verbose = False):
        AbstractLircClient.__init__(self, verbose, None)
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.connect(socketAddress)


class TcpLircClient(AbstractLircClient):

    def __init__(self, address = "localhost", port = DEFAULT_PORT, verbose = False, timeout = None):
        AbstractLircClient.__init__(self, verbose, timeout)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((address, port))
        self._socket.settimeout(timeout)


def newLircClient(commandLineArgs):
    return UnixDomainSocketLircClient(commandLineArgs.socketPathname, commandLineArgs.verbose) \
    if commandLineArgs.address is None else \
    TcpLircClient(commandLineArgs.address, commandLineArgs.port, commandLineArgs.verbose, commandLineArgs.timeout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = 'LircClient')
    parser.add_argument("-a", "--address", help = 'IP name or address of lircd host. Takes preference over --device.', dest='address', default = None)
    socketPath = os.environ['LIRC_SOCKET_PATH'] if 'LIRC_SOCKET_PATH' in os.environ else DEFAULT_LIRC_DEVICE
    parser.add_argument('-d', '--device',  help = 'Path name of the lircd socket', dest = 'socketPathname', default = socketPath)
    parser.add_argument('-p', '--port',    help = 'Port of lircd, default ' + str(DEFAULT_PORT), dest = 'port', default = DEFAULT_PORT, type = int)
    parser.add_argument('-t', '--timeout', help = 'Timeout in milliseconds', dest = 'timeout', type = int, default = None)
    parser.add_argument('-V', '--version', help = 'Display version information for this program', dest = 'versionRequested', action = 'store_true')
    parser.add_argument('-v', '--verbose', help = 'Have some commands executed verbosely', dest = 'verbose', action = 'store_true')

    subparsers = parser.add_subparsers(dest = 'subcommand')

    # Command send_once
    parser_send_once = subparsers.add_parser('send_once', help = 'Send one command')
    parser_send_once.add_argument('-#', '-c', '--count',  help = 'Number of times to send command in send_once', dest = 'count', type = int, default = 1)
    parser_send_once.add_argument('remote',               help = 'Name of remote')
    parser_send_once.add_argument('command',              help = 'Name of command')

    # Command send_start
    parser_send_start = subparsers.add_parser('send_start', help = 'Start sending one command until stopped')
    parser_send_start.add_argument('remote',                help = 'Name of remote')
    parser_send_start.add_argument('command',               help = 'Name of command')
    
    # Command send_stop
    parser_send_stop = subparsers.add_parser('send_stop', help = 'Stop sending the command from send_start')
    parser_send_stop.add_argument('remote',               help = 'remote command')
    parser_send_stop.add_argument('command',              help = 'remote command')

    # Command list
    parser_list = subparsers.add_parser('list',           help = 'Inquire either the list of remotes, or the list of commands in a remote')
    parser_list.add_argument("-c", "--codes",             help = 'List the numerical codes in lircd.conf in addition to the name (as irsend(1) does)', dest = 'codes', action='store_true')
    parser_list.add_argument('remote', nargs = '?',       help = 'Name of remote; empty for a list of remotes')

    # Command set_input_logging
    parser_set_input_log = subparsers.add_parser('set_input_log', help = 'Set input logging')
    parser_set_input_log.add_argument('log_file', nargs = '?', help = 'Path to log file, empty to inhibit logging', default = '')

    # Command set_driver_options
    parser_set_driver_options = subparsers.add_parser('set_driver_options', help = 'Set driver options')
    parser_set_driver_options.add_argument('key',                           help = 'Name of the option')
    parser_set_driver_options.add_argument('value',                         help = 'Value of the option')

    # Command simulate
    parser_simulate = subparsers.add_parser('simulate',                     help = 'Fake the reception of IR signals')
    parser_simulate.add_argument('key',                                     help = 'Name of command to be faked')
    parser_simulate.add_argument('data',                                    help = 'Key press data to be sent to the Lircd')

    # Command set_transmitters
    parser_set_transmitters = subparsers.add_parser('set_transmitters',     help = 'Set transmitters')
    parser_set_transmitters.add_argument('transmitters', nargs='+',         help = "transmitter...")

    # Command version
    parser_version = subparsers.add_parser('version',                       help = 'Inquire version of lircd. (Use --version for the version of THIS program.)')

    args = parser.parse_args()

    if args.versionRequested:
        print(VERSION)
        sys.exit(0)

    lirc = None
    try:
        lirc = newLircClient(args)

        exitstatus = 0

        if args.subcommand == 'send_once':
            lirc.sendIrCommand(args.remote, args.command, args.count - 1)
        elif args.subcommand == 'send_start':
            lirc.sendIrCommandRepeat(args.remote, args.command)
        elif args.subcommand == 'send_stop':
            lirc.stopIr(args.remote, args.command)
        elif args.subcommand == 'list':
            result = lirc.getRemotes() if args.remote is None else lirc.getCommands(args.remote, args.codes);
            for line in result:
                print(line)
        elif args.subcommand == 'set_input_log':
            print("Subcommand not implemented yet, are YOU volunteering?")
            exitstatus = 2
        elif args.subcommand == 'set_driver_options':
            print("Subcommand not implemented yet, are YOU volunteering?")
            exitstatus = 2
        elif args.subcommand == 'simulate':
            print("Subcommand not implemented yet, are YOU volunteering?")
            exitstatus = 2
        elif args.subcommand == 'set_transmitters':
            lirc.setTransmitters(args.transmitters)
        elif args.subcommand == 'version':
            print(lirc.getVersion())
        else:
            print('Unknown subcommand, use --help for syntax.')
            exitstatus = 1

    except LircServerException as ex:
        print("LircServerError: {0}".format(ex))
        exitstatus = 3
    except BadPacketException:
        print("Malformed package received")
        exitstatus = 4
    except ConnectionRefusedError:
        print("Connection refused")
        exitstatus = 5
    except FileNotFoundError as ex:
        print("Could not find {0}".format(args.socketPathname))
        exitstatus = 5
    except PermissionError as ex:
        print("No permission to open {0}".format(args.socketPathname))
        exitstatus = 5

    if lirc is not None:
        lirc.close()

    sys.exit(exitstatus)
