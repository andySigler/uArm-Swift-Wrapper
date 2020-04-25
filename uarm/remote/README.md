# Remote Control

It would be great to be able to control a uArm over a network. This would make it much easier (potentially), to control multiple machines at once, while also making it much easier for programming environments outside of Python to leverage what has already been built here.

This is currently undevelopment and almost completely untested.

## OSC

### Overview

An OSC interface is being developed, to allow a uArm to be controlled over a network.

All methods of the [`SwiftAPIWrapper`](../wrapper/swift_api_wrapper.py) class are made available through this interface, as described in the [`swift_api_wrapper_osc.json`](./swift_api_wrapper_osc.json) file.

### Server

To run the OSC server, first power on the uArm and connect it to the host computer over USB

Run the command:

```
python -m uarm.remote
```

The server will automically connect to a uArm over USB, and listen for OSC messages on IP `127.0.0.1` and port `5115`.

To select a different IP and/or port, using the following arguments:

```
python -m uarm.remote --ip 192.168.1.2 --port 8080
```

### Client

Currently no OSC client has been written for controlling the uArm. I plan to build a first pass at this in NodeJS.

You can see an small test of what a client needs to do within [`uarm.remote.__main__`](./__main__.py) when the `--test` flag is set:

```
python -m uarm.remote --test
```
