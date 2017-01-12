# Copyright (C) 2017 Alec Leamas.

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

import enum


class BadPacketException(Exception):
    ''' This exception is thrown when a communication error occurs. '''
    pass


class Result(enum.Enum):
    ''' Public reply parser result, available when completed. '''
    OK = 1
    FAIL = 2
    INCOMPLETE = 3


class ReplyParser(object):
    '''
    Handles parsing of reply packet. Public accessors:
       - result: Enum Result, reflects parser state.
       - success: boolean, reflects SUCCESS/ERROR.
       - data: List of lines, the command DATA payload.
       - sighup: boolean, reflects if SIGHUP package has been received
         (these are otherwise ignored)
       - last_line: string, last input line (for error messages).
       - is_completed: True if no more input is required.
    '''

    def __init__(self):
        self.result = Result.INCOMPLETE
        self.success = None
        self.data = []
        self.last_line = ""
        self.sighup = False
        self._state = self._State.BEGIN
        self._lines_expected = None
        self._buffer = bytearray(0)

    @property
    def is_completed(self):
        ''' Returns true if no more reply input is required. '''
        return self.result != Result.INCOMPLETE

    def feed(self, line):
        ''' Enter a line of data into parsing FSM, update state. '''

        fsm = {
            self._State.BEGIN: self._begin,
            self._State.COMMAND: self._command,
            self._State.RESULT: self._result,
            self._State.DATA: self._data,
            self._State.LINE_COUNT: self._line_count,
            self._State.LINES: self._lines,
            self._State.END: self._end,
            self._State.SIGHUP_END: self._sighup_end
        }
        line = line.strip()
        if not line:
            return
        self.last_line = line
        fsm[self._state](line)
        if self._state == self._State.DONE:
            self.result = Result.OK

    ##
    #  @defgroup FSM Internal parser FSM
    #  @{
    #  pylint: disable=missing-docstring,redefined-variable-type

    class _State(enum.Enum):
        ''' Internal FSM state. '''
        BEGIN = 1
        COMMAND = 2
        RESULT = 3
        DATA = 4
        LINE_COUNT = 5
        LINES = 6
        END = 7
        DONE = 8
        NO_DATA = 9
        SIGHUP_END = 10

    def _bad_packet_exception(self, line):
        raise BadPacketException(
            "Cannot parse: %s\nat state: %s\n" % (line, self._state))

    def _begin(self, line):
        if line == "BEGIN":
            self._state = self._State.COMMAND

    def _command(self, line):
        if not line:
            self._bad_packet_exception(line)
        self._state = self._State.RESULT

    def _result(self, line):
        if line in ["SUCCESS", "ERROR"]:
            self.success = line == "SUCCESS"
            self._state = self._State.DATA
        elif line == "SIGHUP":
            self._state = self._State.SIGHUP_END
            self.sighup = True
        else:
            self._bad_packet_exception(line)

    def _data(self, line):
        if line == "END":
            self._state = self._State.DONE
        elif line == "DATA":
            self._state = self._State.LINE_COUNT
        else:
            self._bad_packet_exception(line)

    def _line_count(self, line):
        try:
            self._lines_expected = int(line)
        except ValueError:
            self._bad_packet_exception(line)
        if self._lines_expected == 0:
            self._state = self._State.END
        else:
            self._state = self._State.LINES

    def _lines(self, line):
        self.data.append(line)
        if len(self.data) >= self._lines_expected:
            self._state = self._State.END

    def _end(self, line):
        if line != "END":
            self._bad_packet_exception(line)
        self._state = self._State.DONE

    def _sighup_end(self, line):
        if line == "END":
            self._state = self._State.BEGIN
        else:
            self._bad_packet_exception(line)
