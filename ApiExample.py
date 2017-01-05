#! /usr/bin/python3

# Copyright (C) 2017 Bengt Martensson.
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# You should have received a copy of the GNU General Public License along with
# this program. If not, see http://www.gnu.org/licenses/.


"""
An somewhat silly example of using the API of LircClient to send and receive information from a Lirc server.
"""

from LircClient import UnixDomainSocketLircClient

lirc = UnixDomainSocketLircClient()
#lirc.setVerbosity(True)
version = lirc.getVersion()
print("Version: {0}".format(version))
remotes = lirc.getRemotes()
i = 0
for remote in remotes:
    print(str(i) + ":\t" + remote);
    i = i+1

remoteNo = int(input("Select a remote by entering its number: "))
remote = remotes[remoteNo]
commands = lirc.getCommands(remote)
i = 0
for command in commands:
    print(str(i) + ":\t" + command)
    i = i+1

commandNo = int(input("Select a command by entering its number: "))
command = commands[commandNo]
lirc.sendIrCommand(remote, command, 1);
