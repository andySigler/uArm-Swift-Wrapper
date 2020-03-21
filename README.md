# uArm Python Wrapper

![uArm-Swift-Pro](doc/uarm-swift-pro.jpg)

## Overview

This project is a fork and thin wrapper around the [uArm-Python-SDK](https://github.com/uArm-Developer/uArm-Python-SDK) from uFactory. The goal of this fork is to create a more intuitive and easier to use set of controls for the [uArm Swift/SwiftPro](https://store.ufactory.cc/products/uarm), built on-top of the original Python API from uFactory.

```python
robot = uarm_scan_and_connect()
robot.home()
robot.move_to(x=150, y=20, z=10)
robot.pump(True)
robot.move_relative(y=-40, z=60)
robot.pump(False)
robot.sleep()
```

Because this wrapper inherits from the original Python SDK from uFactory, all of their methods and functionalities are still available through this interface.

## Features

List of current features on my mind. As new features are thought of, I'll add them here.

- Movement
    - [x] Absolute and relative movements
    - [x] Can detect valid coordinates for the uArm
    - [x] Near accurate millimeter speed and acceleration control
    - [x] Push/pop speed settings
    - [x] Rotating wrist servo motor
    - [x] Pump or grip commands, with timing to ensure command has finished
- Control
    - [x] Read and update coordinates
    - [x] Home method for moving to reliable position
    - [x] Enable and disable stepper motors, all and individually
    - [x] Simulation mode, for testing scripts with running on physical device
    - [ ] Control over OSC
    - [x] Chainable class methods
    - [x] Use encoders to detect when the uArm is touched by a user
- Misc
    - [x] Works alongside original uArm-Python-SDK
    - [x] Examples for basic wrapper methods
    - [ ] Examples for controlling over OSC (Processing, P5.js, Max/MSP/Jitter, Node, etc.)

## Examples

Some simple examples are included to show how the API wrapper can easily be used for simple movements and controls of the uArm Swift Pro:

- [Connecting to a uArm](examples/api-wrapper/connect.py)
- [Simulate for Unplugged Testing](examples/api-wrapper/simulate.py)
- [Move the Arm](examples/api-wrapper/move_arm.py)
- [Speed and Acceleration](examples/api-wrapper/speed_acceleration.py)
- [Push/Pop the Speed Settings](examples/api-wrapper/speed_acceleration.py)
- [Rotate the Wrist](examples/api-wrapper/rotate_wrist.py)
- [Pick Up Items](examples/api-wrapper/pick_up.py)
- [Disable the Motors](examples/api-wrapper/disable_motors.py)
- [Read the Position](examples/api-wrapper/position.py)
- [Chaining Commands](examples/api-wrapper/command_chaining.py)
- [Using Original SwiftAPI Commands](examples/api-wrapper/original_swift_api.py)

(The original examples by uFactory [can be found here](examples/api/))

## Documentation

The [API reference documentation can be found here](doc/api/swift_api_wrapper.md), which include methods and attributes of the `SwiftAPIWrapper` class. (The original API documentation by uFactory for their `SwiftAPI` class [can be found here](doc/api/swift_api.md))

This repository also include PDF guides distrubuted by uFactory, which are located in [this folder](doc/manuals).

## Installation

You can install through pip, or by cloning this repository and installing locally.

To install through pip, run:
```
pip install git+git://github.com/andySigler/uArm-Swift-Wrapper.git@master#egg=uArm-Swift-Wrapper
```

To install by cloning the repository, run:
```
git clone https://github.com/andySigler/uArm-Swift-Wrapper.git
cd uArm-Swift-Wrapper
python setup.py install
```

## Firmware Update

For consistancy, this Python wrapper requires the connected uArm Swift Pro to have firmware verion `4.5.0` flashed to the device. To help, this repository includes a script for updating a connected uArm Swift Pro to version `4.5.0`.

First, the script uses `avrdude` to flash the firmware to the uArm at the specified port. If you do not have `avrdude` already installed, you can install using Homebrew as follows:

```
brew install avrdude
```

Second, connect the uArm to your computer over USB and power the uArm on.

Finally, run the script:

```
bin/firmware/flash <PORT>`
```

The `<PORT>` argument is the name of the serial port the uArm occupies on your operating system. For example, on my Macbook, the command looks like:

```
bin/firmware/flash /dev/tty.usbmodem1417501
```

Or on Windows:

```
bin/firmware/flash COM2
```

## License
uArm-Python-SDK is published under the [BSD license](https://en.wikipedia.org/wiki/BSD_licenses)
