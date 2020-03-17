# uArm-Python-SDK [Extended]

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

## Installation

You can install through pip, or by cloning this repository and installing locally.

To install through pip, run:
```
pip install git+git://github.com/andySigler/uArm-Python-SDK.git@uarm-extended#egg=uArm-Python-SDK
```

To install by cloning the repository, run:
```
git clone https://github.com/andySigler/uArm-Python-SDK.git
cd uArm-Python-SDK
git checkout uarm-extended
python setup.py install
```

## Examples

- [Connecting to a uArm](examples/api-extended/connect.py)
- [Simulate for Unplugged Testing](examples/api-extended/simulate.py)
- [Move the Arm](examples/api-extended/move_arm.py)
- [Speed and Acceleration](examples/api-extended/speed_acceleration.py)
- [Push/Pop the Speed Settings](examples/api-extended/speed_acceleration.py)
- [Rotate the Wrist](examples/api-extended/rotate_wrist.py)
- [Pick Up Items](examples/api-extended/pick_up.py)
- [Disable the Motors](examples/api-extended/disable_motors.py)
- [Read the Position](examples/api-extended/position.py)
- [Chaining Commands](examples/api-extended/command_chaining.py)
- [Using Original SwiftAPI Commands](examples/api-extended/original_swift_api.py)

(The original examples by uFactory [can be found here](examples/api/))

## Documentation

[Read the API reference documentation](doc/api/swift_api_extended.md)

(The original API documentation by uFactory for their `SwiftAPI` class [can be found here](doc/api/swift_api.md))

## License
uArm-Python-SDK is published under the [BSD license](https://en.wikipedia.org/wiki/BSD_licenses)
