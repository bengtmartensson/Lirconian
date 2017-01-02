# PythonLircClient
This is a new and independent implementation of the Lirc `irsend` program. It offers
a Python API and a command line interface. The command line interface is almost,
but not quite, compatible with `irsend`. Instead, it is organized as a program
with subcommands, `send_once`, etc.

There are some other subtile differences from `irsend`:

* subcommand must be lower case,
* `send_once` only takes one command (`irsend` takes several),
* `send_stop` without arguments uses the `remote` and the `command` from the last `send_start` command,
* no need to give dummy empty arguments for `list`,
* The `--count` argument to `send_once` is argument to the subcommand.
* the code in `list remote` is suppressed, unless `-c` is given,
* port number must be given with the `--port` (`-p`) argument; `hostip:portnumber` is not recognized,
* verbose option `--verbose` (`-v`)
* selectable timeout with `--timeout` (`-t`) option
* better error messages

The subcommands `set_input_log`, `set_driver_options`, and `simulate` are presently not
implemented. (The first two are not documented for `irsend` anyhow...).
Help is welcome.

Python3 only.
It does not depend on anything but standard Python libraries.

For a GUI version, look at IrScrutinizer.
For a Java version, look at [JavaLircClient](https://github.com/bengtmartensson/JavaLircClient)

## Usage:

    usage: LircClient [-h] [-a ADDRESS] [-d SOCKETPATHNAME] [-p PORT] [-t TIMEOUT]
		      [-V] [-v]
		      {send_once,send_start,send_stop,list,set_input_log,set_driver_options,simulate,set_transmitters,version}
		      ...

    positional arguments:
      {send_once,send_start,send_stop,list,set_input_log,set_driver_options,simulate,set_transmitters,version}
	send_once           Send one command
	send_start          Start sending one command until stopped
	send_stop           Stop sending the command from send_start
	list                Inquire either the list of remotes, or the list of
			    commands in a remote
	set_input_log       Set input logging
	set_driver_options  Set driver options
	simulate            Fake the reception of IR signals
	set_transmitters    Set transmitters
	version             Inquire version of lircd. (Use --version for the
			    version of THIS program.)

    optional arguments:
      -h, --help            show this help message and exit
      -a ADDRESS, --address ADDRESS
			    IP name or address of lircd host. Takes preference
			    over --device.
      -d SOCKETPATHNAME, --device SOCKETPATHNAME
			    Path name of the lircd socket
      -p PORT, --port PORT  Port of lircd, default 8765
      -t TIMEOUT, --timeout TIMEOUT
			    Timeout in milliseconds, default 5000
      -V, --version         Display version information for this program
      -v, --verbose         Have some commands executed verbosely
