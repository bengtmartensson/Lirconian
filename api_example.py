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
An somewhat silly example of using the API of LircClient to send and
receive information from a Lirc server.
"""

from lirc_client import UnixDomainSocketLircClient

lirc = UnixDomainSocketLircClient()
# Uncomment if desired
# lirc.setVerbosity(True)
version = lirc.get_version()
print("Version: {0}".format(version))
remotes = lirc.get_remotes()
i = 0
for remote in remotes:
    print(str(i) + ":\t" + remote)
    i = i + 1

remote_no = int(input("Select a remote by entering its number: "))
remote = remotes[remote_no]
commands = lirc.get_commands(remote)
i = 0
for command in commands:
    print(str(i) + ":\t" + command)
    i = i + 1

command_no = int(input("Select a command by entering its number: "))
command = commands[command_no]
lirc.send_ir_command(remote, command, 1)
