Python Library Documentation: function uarm_create in module uarm.wrapper.swift_api_wrapper

#### def uarm_create(verbose=False, verbose_serial=False, **kwargs):

```
Helper method for creating instances of SwiftAPIWrapper
:param verbose: If True, enables SwiftAPIWrapper printing of debug messages
:param verbose_serial: If True, enables printing of all GCode messages sent over serial
:return: instance of SwiftAPIWrapper
```
Python Library Documentation: function uarm_scan in module uarm.wrapper.swift_api_wrapper

#### def uarm_scan(verbose=False, verbose_serial=False, **kwargs):

```
Helper method for discovering serial ports for, and creating instances of, SwiftAPIWrapper
:param verbose: If True, enables SwiftAPIWrapper printing of debug messages
:param verbose_serial: If True, enables printing of all GCode messages sent over serial
:return: list of disconnected instances of SwiftAPIWrapper, found connected over a serial port
```
Python Library Documentation: function uarm_scan_and_connect in module uarm.wrapper.swift_api_wrapper

#### def uarm_scan_and_connect(verbose=False, verbose_serial=False, **kwargs):

```
Helper method for discovering serial port, creating instances, and connecting to SwiftAPIWrapper
:param verbose: If True, enables SwiftAPIWrapper printing of debug messages
:param verbose_serial: If True, enables printing of all GCode messages sent over serial
:return: Connected instance of SwiftAPIWrapper, found connected over a serial port
```
Python Library Documentation: class SwiftAPIWrapper in module uarm.wrapper.swift_api_wrapper

## class SwiftAPIWrapper
****************************************

### descriptors
****************************************
#### port
Get the serial port of the connected uArm device
:return: The serial port as a string, or "unknown" is none was set

#### position
Get the current XYZ coordinate position
:return: Dictionary with keys "x", "y", and "z", and float values for millimeter positions

#### wrist_angle
Retrieve the current wrist angle of the servo motor
:return: Angle in degrees, 90 is center

### methods
****************************************
#### def __init__(self, connect=False, simulate=False, **kwargs):

```
The API wrapper of SwiftAPI, which in turn wraps the Swift and SwiftPro
:param connect: If True, will auto-connect to the serial port
:param simulate: If True, this instance will not connect to serial port, but will process all methods pretending that is is connected to a uArm
:param port: optional, the serial port of the uArm as appears on the OS
:return: Instance of SwiftAPIWrapper
```

#### def acceleration(self, acceleration):

```
Set the acceleration of the connected uArm device, in psuedo millimeters/second/second
:return: self
```

#### def connect(self, *args, **kwargs):

```
Connect to the serial port of the connected uArm device
:return: self
```

#### def disable_all_motors(self):

```
Turn off all the connected uArm's stepper motors
:return: self
```

#### def disable_base(self):

```
Turn off the connected uArm's base stepper motor
:return: self
```

#### def disconnect(self, *args, **kwargs):

```
Disconnect from the serial port of the connected uArm device
:return: self
```

#### def enable_all_motors(self):

```
Turn on all the connected uArm's stepper motors
:return: self
```

#### def get_base_angle(self):

```
Retrieve the current angle in degrees of the base motor from the connected uArm device
:return: angle in degrees, 90 is center
```

#### def grip(self, enable, sleep=None):

```
Turn on all the connected uArm's stepper motors
:param enable: If True the gripper turns on, else if False the gripper turns off
:param sleep: (optional) number of seconds to wait after the sending the command, default is 2 seconds
:return: self
```

#### def home(self):

```
Reset the connected uArm device, and move it to a safe position, one axis at a time
:return: self
```

#### def is_pressing(self):

```
Check to see if the pump's limit switch is being pressed
:return: True if the switch is pressed, else False
```

#### def is_simulating(self):

```
Check whether this instance of SwiftAPIWrapper is simulating or not
:return: True is simulating, else False
```

#### def mode(self, new_mode):

```
Set the uArm device mode
:param new_mode: Can be either "general" or "pen_gripper"
:return: self
```

#### def move_relative(self, x=None, y=None, z=None, check=False):

```
Move to a relative cartesian coordinate, away from it's current coordinate
:param x: Cartesian millimeter of the X axis, if None then uses current position
:param y: Cartesian millimeter of the Y axis, if None then uses current position
:param z: Cartesian millimeter of the Z axis, if None then uses current position
:param check: If True, asks the connected uArm device if the target coordinate is within its range of movement
:return: self
```

#### def move_to(self, x=None, y=None, z=None, check=False):

```
Move to an absolute cartesian coordinate
:param x: Cartesian millimeter of the X axis, if None then uses current position
:param y: Cartesian millimeter of the Y axis, if None then uses current position
:param z: Cartesian millimeter of the Z axis, if None then uses current position
:param check: If True, asks the connected uArm device if the target coordinate is within its range of movement
:return: self
```

#### def pop_settings(self):

```
Retrieve the latest pushed speed and accleration values, and set them to the connected uArm device
:return: self
```

#### def probe(self, step=1, speed=10):

```
Move the connected uArm device down until the pump's limit switch is being pressed
:param step: number of millimeter to move before checking, default is 1 millimeter
:param speed: speed to move while probing, default is 10mm/sec
:return: self
```

#### def pump(self, enable, sleep=None):

```
Turn on all the connected uArm's stepper motors
:param enable: If True the pump turns on, else if False the pump turns off
:param sleep: (optional) number of seconds to wait after the sending the command, default is 0.2 seconds
:return: self
```

#### def push_settings(self):

```
Save the current speed and accleration values, for retrieval later by `pop_settings()`
:return: self
```

#### def rotate_relative(self, angle=0, sleep=0.25, wait=True):

```
Rotate the wrist's servo motor by a relative angle, in degrees
:param angle: The relative amount to rotate the servo angle in degrees
:param sleep: The number of seconds to wait after setting the angle, default is 0.25 seconds
:param wait: If True, will wait for the connected uArm device to finish processing the command
:return: self
```

#### def rotate_to(self, angle=90, sleep=0.25, wait=True):

```
Rotate the wrist's servo motor to a angle, in degrees
:param angle: The target servo angle in degrees, 90 is center
:param sleep: The number of seconds to wait after setting the angle, default is 0.25 seconds
:param wait: If True, will wait for the connected uArm device to finish processing the command
:return: self
```

#### def sleep(self):

```
Home the connected uArm device, and then disable all motors
:return: self
```

#### def speed(self, speed):

```
Set the speed of the connected uArm device, in psuedo millimeters/second
:return: self
```

#### def update_position(self):

```
Retrieve the current XYZ coordinate position from the connected uArm device
:return: self
```

#### def wait_for_arrival(self, timeout=10, set_pos=True):

```
Wait for all asynchronous commands and movements to finish
:param timeout: maximum number of seconds to wait
:param set_pos: If True, the target position will be resent as a move command until is has been arrived to
:return: self
```

#### def wait_for_touch(self, distance=None, timeout=None):

```
Monitor the position of all motors to detect if the uArm has been touched, potentially moving one of the axes slightly
:param distance: number of millimeter to move to trigger a touch event, default is 0.25 millimeters
:param timeout: number of seconds to wait for a touch event, default is forever
:return: self
```
