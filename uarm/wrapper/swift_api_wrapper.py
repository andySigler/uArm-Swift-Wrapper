import copy
import json
import logging
import math
import os
import time

from serial.tools.list_ports import comports

from uarm.offset.helpers import cartesian_to_polar
from uarm.offset.helpers import round_position
from uarm.offset.helpers import subtract_positions
from uarm.record import Recorder
import uarm.swift.protocol as PROTOCOL
from uarm.wrapper import SwiftAPI


logger = logging.getLogger('uarm.swiftapi.wrapper')

# DEVICE INFO
UARM_DEVICE_TYPE = 'SwiftPro'
UARM_ALLOWED_FIRMWARE_VERSIONS = ['4.5.0']

# SERIAL PORT
UARM_USB_HWID = '2341:0042'

# MODE (end-tool)
# COORDINATE MODES
UARM_DEFAULT_MODE = 'general'
UARM_MODE_TO_CODE = {
  'general': 0,
  'laser': 1,
  '3d_printer': 2,
  'pen_gripper': 3
}
UARM_CODE_TO_MODE = {
  val: key
  for key, val in UARM_MODE_TO_CODE.items()
}

UARM_MOTOR_IDS = {
  'base': PROTOCOL.SERVO_BOTTOM,
  'shoulder': PROTOCOL.SERVO_LEFT,
  'elbow': PROTOCOL.SERVO_RIGHT,
  'wrist': PROTOCOL.SERVO_HAND
}

# SPEED
UARM_DEFAULT_SPEED_FACTOR = 0.007 # was found to make mm/sec near accurate
UARM_MAX_SPEED = 600
UARM_MIN_SPEED = 1
UARM_DEFAULT_SPEED = 150

# ACCELERATION
UARM_MAX_ACCELERATION = 50
UARM_MIN_ACCELERATION = 0.01
UARM_DEFAULT_ACCELERATION = 5

# DETECTING SKIPPED STEPS
UARM_SKIPPED_DISTANCE_THRESHOLD = 1.5

# WRIST ANGLE
UARM_MIN_WRIST_ANGLE = 0
UARM_MAX_WRIST_ANGLE = 180
UARM_DEFAULT_WRIST_ANGLE = 90
UARM_DEFAULT_WRIST_SLEEP = 0.25

# PUMP & GRIP
UARM_DEFAULT_PUMP_SLEEP = {True: 0.2, False: 0.2}
UARM_DEFAULT_GRIP_SLEEP = {True: 0, False: 2.0}
UARM_HOLDING_CODES = ['off', 'empty', 'holding']

# HOMING
UARM_HOME_SPEED = 200
UARM_HOME_ACCELERATION = 1.3
UARM_HOME_START_POS = {'x': 200, 'y': 0, 'z': 150}
UARM_HOME_ORDER = [0, 1, 2] # base=0, shoulder=1, elbow=2
UARM_HOME_ANGLE = [90.0, 118, 50]
UARM_HOME_SIMULATE_POS = {'x': 120, 'y': 0, 'z': 30}

# PROBING
UARM_DEFAULT_PROBE_SPEED = 10
UARM_DEFAULT_PROBE_ACCELERATION = 1.3
UARM_DEFAULT_PROBE_STEP = 1

# TOUCH DETECT
UARM_DEFAULT_TOUCH_THRESH_MM = 0.25

# SAVED HARDWARE SETTINGS
UARM_HARDWARE_SETTINGS_FILE_NAME = 'uarm_hardware_settings.json'
UARM_HARDWARE_SETTINGS_DIRECTORY = '.hardware_settings'
UARM_HARDWARE_SETTINGS_ADDRESS_START = 0 # arbitrary
UARM_HARDWARE_SETTINGS_ADDRESS_OFFSET = 10
UARM_DEFAULT_HARDWARE_SETTINGS = {
  'id': 'simulate',
  'z_offset': 0,
  'mode': copy.copy(UARM_MODE_TO_CODE['general']),
  'wrist_offset': 0
}

# SAVED RECORDINGS
UARM_HARDWARE_RECORDINGS_FILE_NAME = 'uarm_recordings.json'


def _is_uarm_port(port_info):
  return (port_info.hwid and UARM_USB_HWID in port_info.hwid)


def _serial_log_port_info(port_info):
  logger.debug('- Port: {0}'.format(port_info.device))
  for key, val in port_info.__dict__.items():
    if (key != 'device' and val and val != 'n/a'):
      logger.debug('\t- {0}: {1}'.format(key, val))


def _get_uarm_ports():
  found_ports = []
  for p in comports():
    _serial_log_port_info(p)
    if _is_uarm_port(p):
      found_ports.append(p)
  return found_ports


def uarm_create(**kwargs):
  """
  Helper method for creating instances of SwiftAPIWrapper
  :param port: Serial port of the uArm
  :param connect: If True, will auto-connect to serial port
  :param print_gcode: If True, enables printing of all GCode messages sent over serial
  :return: instance of SwiftAPIWrapper
  """
  return SwiftAPIWrapper(**kwargs)


def uarm_scan(print_gcode=False, **kwargs):
  """
  Helper method for discovering serial ports for, and creating instances of, SwiftAPIWrapper
  :param print_gcode: If True, enables printing of all GCode messages sent over serial
  :return: list of disconnected instances of SwiftAPIWrapper, found connected over a serial port
  """
  found_swifts = []
  for port_info in _get_uarm_ports():
    try:
      swift = uarm_create(
          port=port_info.device,
          connect=False,
          print_gcode=print_gcode,
          **kwargs)
      found_swifts.append(swift)
    except Exception as e:
      logger.exception('Exception while running uarm_create()')
  if len(found_swifts):
    return found_swifts
  raise RuntimeError('Unable to find uArm ports')


def uarm_scan_and_connect(print_gcode=False, hwid=None, **kwargs):
  """
  Helper method for discovering serial port, creating instances, and connecting to SwiftAPIWrapper
  :param print_gcode: If True, enables printing of all GCode messages sent over serial
  :return: Connected instance of SwiftAPIWrapper, found connected over a serial port
  """
  c_swift = None
  for swift in uarm_scan(print_gcode=print_gcode, **kwargs):
    try:
      swift.connect()
      if hwid is not None and swift.hardware_settings['id'] != hwid:
        swift.disconnect()
        continue
      c_swift = swift
      break
    except Exception as e:
      logger.exception(
        'Error connecting to uArm on port: {0}'.format(swift.port))
      continue
  if c_swift:
    logger.debug('Connected to uArm on port: {0}'.format(c_swift.port))
    for key, val in c_swift.get_device_info().items():
      logger.debug('\t- {0}: {1}'.format(key, val))
    return c_swift
  raise RuntimeError('Unable to find uArm port')


class SwiftAPIWrapper(SwiftAPI):

  def __init__(self,
               port='simulate',
               settings_dir=None,
               connect=False,
               simulate=False,
               print_gcode=False,
               **kwargs):

    """
    The API wrapper of SwiftAPI, which in turn wraps the Swift and SwiftPro
    :param port: optional, the serial port of the uArm as appears on the OS
    :param connect: If True, will auto-connect to the serial port
    :param simulate: If True, this instance will not connect to serial port, but will process all methods pretending that is is connected to a uArm
    :param print_gcode: If True, all GCodes sent over serial are printed
    :return: Instance of SwiftAPIWrapper
    """

    '''
    connect: during instantiation, should connect to serial port
    simulate: makes this class intance unable to connect, only simulates
    '''

    self._enabled = False  # safer to assume motors are disabled
    self._simulating = simulate
    self._port = port

    # run update_position() to get real position from uArm
    self._pos = UARM_HOME_SIMULATE_POS.copy()
    self._wrist_angle = UARM_DEFAULT_WRIST_ANGLE

    self._speed = UARM_DEFAULT_SPEED
    self._acceleration = UARM_DEFAULT_ACCELERATION
    self._pushed_speed = []
    self._pushed_acceleration = []

    self._hardware_settings = copy.deepcopy(UARM_DEFAULT_HARDWARE_SETTINGS)
    self._hardware_settings_dir = None

    self._recorder = None

    super().__init__(do_not_open=True, print_gcode=print_gcode, port=port, **kwargs)
    if settings_dir:
      self.set_settings_directory(settings_dir)
    if connect:
      self.connect()
    elif simulate:
      self._setup()

  '''
  SETTINGS, UTILS, and MODES
  '''

  @property
  def port(self):
    """
    Get the serial port of the connected uArm device
    :return: The serial port as a string, or "unknown" is none was set
    """
    return self._port

  def connect(self, *args, **kwargs):
    """
    Connect to the serial port of the connected uArm device
    :return: self
    """
    logger.debug('connect')
    if self.is_simulating():
      raise RuntimeError(
        'uArm is in \"simulate\" mode, cannot connect to device')
    super().connect(*args, **kwargs)
    self.waiting_ready(timeout=3)
    if kwargs.get('port'):
      self._port = kwargs.get('port')
    self._test_device_info()
    self._setup()
    return self

  def disconnect(self, *args, **kwargs):
    """
    Disconnect from the serial port of the connected uArm device
    :return: self
    """
    logger.debug('disconnect')
    if self.is_simulating():
      raise RuntimeError(
        'uArm is in \"simulate\" mode, cannot disconnect from device')
    super().disconnect(*args, **kwargs)
    return self

  def is_simulating(self):
    """
    Check whether this instance of SwiftAPIWrapper is simulating or not
    :return: True is simulating, else False
    """
    return bool(self._simulating)

  def _test_device_info(self):
    logger.debug('_test_device_info')
    if self.is_simulating():
      raise RuntimeError(
        'uArm is in \"simulate\" mode, cannot test device info')
    info = self.get_device_info()
    logger.debug(info)
    dt = info.get('device_type')
    if not dt or dt != UARM_DEVICE_TYPE:
      raise RuntimeError('Device type should be {0}, but got {1}'.format(
        UARM_DEVICE_TYPE, dt))
    fw = info.get('firmware_version')
    if not fw or fw not in UARM_ALLOWED_FIRMWARE_VERSIONS:
      raise RuntimeError('Device FW version {0} not within {1}'.format(
        fw, UARM_ALLOWED_FIRMWARE_VERSIONS))
    hw_id = info.get('device_unique')
    if not hw_id:
      raise RuntimeError('Device HW ID not accessible')
    self._hardware_settings['id'] = hw_id
    return self

  def _setup(self):
    logger.debug('_setup')
    if not self.is_simulating():
      self.flush_cmd()
      self.waiting_ready()
      self._init_settings()
    self.set_speed_factor(UARM_DEFAULT_SPEED_FACTOR)
    self.tool_mode(self.hardware_settings['mode'])
    self.rotate_to(UARM_DEFAULT_WRIST_ANGLE)
    return self

  def push_settings(self):
    """
    Save the current speed and accleration values, for retrieval later by `pop_settings()`
    :return: self
    """
    self._pushed_speed.append(float(self._speed))
    self._pushed_acceleration.append(float(self._acceleration))
    return self

  def pop_settings(self):
    """
    Retrieve the latest pushed speed and accleration values, and set them to the connected uArm device
    :return: self
    """
    if len(self._pushed_speed) == 0 or len(self._pushed_acceleration) == 0:
      raise RuntimeError('Cannot "pop" settings when none have been "pushed"')
    self.speed(float(self._pushed_speed[-1]))
    self._pushed_speed = self._pushed_speed[:-1]
    self.acceleration(float(self._pushed_acceleration[-1]))
    self._pushed_acceleration = self._pushed_acceleration[:-1]
    return self

  def wait_for_arrival(self, timeout=10, check=True):
    """
    Wait for all asynchronous commands and movements to finish
    :param timeout: maximum number of seconds to wait
    :param set_pos: If True, the target position will be resent as a move command until is has been arrived to
    :return: self
    """
    logger.debug('wait')
    if self.is_simulating():
      return self
    start_time = time.time()
    if self.flush_cmd(timeout=timeout, wait_stop=True) != PROTOCOL.OK:
      raise TimeoutError(
        'Unable to arrive within {1} seconds'.format(timeout))
    self.update_position(check=check)
    return self

  def tool_mode(self, new_mode='general'):
    """
    Set the uArm device mode
    :param new_mode: Can be either "general" or "pen_gripper"
    :return: self
    """
    if isinstance(new_mode, int):
      new_mode = UARM_CODE_TO_MODE.get(new_mode)
    logger.debug('mode: {0}'.format(new_mode))
    if new_mode not in UARM_MODE_TO_CODE.keys():
      raise ValueError('Unknown mode: {0}'.format(new_mode))
    self.save_hardware_settings(mode=new_mode)
    if not self.is_simulating():
      self.set_mode(UARM_MODE_TO_CODE[new_mode])
    self.update_position()
    return self

  def get_tool_mode(self):
    return self.hardware_settings['mode']

  def speed(self, speed=UARM_DEFAULT_SPEED):
    """
    Set the speed of the connected uArm device, in psuedo millimeters/second
    :return: self
    """
    logger.debug('speed: {0}'.format(speed))
    if speed < UARM_MIN_SPEED:
      speed = UARM_MIN_SPEED
      logger.debug('speed changed to: {0}'.format(speed))
    if speed > UARM_MAX_SPEED:
      speed = UARM_MAX_SPEED
      logger.debug('speed changed to: {0}'.format(speed))
    self._speed = speed
    return self

  def acceleration(self, acceleration=UARM_DEFAULT_ACCELERATION):
    """
    Set the acceleration of the connected uArm device, in psuedo millimeters/second/second
    :return: self
    """
    logger.debug('acceleration: {0}'.format(acceleration))
    if acceleration < UARM_MIN_ACCELERATION:
      acceleration = UARM_MIN_ACCELERATION
      logger.debug('acceleration changed to: {0}'.format(acceleration))
    if acceleration > UARM_MAX_ACCELERATION:
      acceleration = UARM_MAX_ACCELERATION
      logger.debug('acceleration changed to: {0}'.format(acceleration))
    self._acceleration = acceleration
    if not self.is_simulating():
      self.set_acceleration(acc=self._acceleration)
    return self

  def _apply_z_offset(self, pos):
    pos['z'] += self.hardware_settings['z_offset']
    return pos

  def _remove_z_offset(self, pos):
    pos['z'] -= self.hardware_settings['z_offset']
    return pos

  def update_position(self, check=False):
    """
    Retrieve the current XYZ coordinate position from the connected uArm device
    :return: self
    """
    logger.debug('update_position')
    if self.is_simulating():
      return self
    pos = self.get_position(wait=True)
    is_n = pos is None
    is_l = isinstance(pos, list)
    if is_n or not is_l or not len(pos) or not isinstance(pos[0], float):
      logger.debug('Not able to read position, out of bounds')
      return self
    new_pos = round_position(self._apply_z_offset({
      'x': pos[0],
      'y': pos[1],
      'z': pos[2]
    }))
    distance = 0
    check = check and self._enabled  # no need to check if motors are disabled
    if check:
      old_pos = self._pos.copy()
      distance, _, _ = cartesian_to_polar(
        **subtract_positions(new_pos, old_pos))
    self._pos = new_pos
    if check and distance > UARM_SKIPPED_DISTANCE_THRESHOLD:
      raise RuntimeError(
        'Detected {0}mm skipped: target={1} - actual={2}'.format(
          round(distance, 1), old_pos, new_pos))
    logger.debug('New Position: {0}'.format(self._pos))
    return self

  def get_base_angle(self):
    """
    Retrieve the current angle in degrees of the base motor from the connected uArm device
    :return: angle in degrees, 90 is center
    """
    # this shouldn't be calculated but instead retrieved from device
    # because there could be an offset applied to the endtool, which determines
    # the cartesian coordinate position
    degree = self.get_servo_angle(UARM_MOTOR_IDS['base'])
    # map angle to match Y cartesian behavior (center=0, +Y=+Angle, etc.)
    degree = (90 - degree) * -1
    radian = round((degree / 180) * math.pi, 3)
    return radian

  @property
  def position(self):
    """
    Get the current XYZ coordinate position
    :return: Dictionary with keys "x", "y", and "z", and float values for millimeter positions
    """
    return copy.copy(self._pos)

  @property
  def wrist_angle(self):
    """
    Retrieve the current wrist angle of the servo motor
    :return: Angle in degrees, 90 is center
    """
    return copy.copy(self._wrist_angle)

  def _set_wrist_offset(self, wrist_offset=0):
    real_angle = self.wrist_angle + self.hardware_settings['wrist_offset']
    self.save_hardware_settings(wrist_offset=wrist_offset)
    self._wrist_angle = real_angle - self.hardware_settings['wrist_offset']
    return self

  def wrist_offset_reset(self):
    self._set_wrist_offset(wrist_offset=0)
    return self

  def wrist_is_centered(self):
    real_angle = self.wrist_angle + self.hardware_settings['wrist_offset']
    wrist_offset = real_angle - UARM_DEFAULT_WRIST_ANGLE
    self._set_wrist_offset(wrist_offset=wrist_offset)
    return self

  @property
  def hardware_settings(self):
    return copy.deepcopy(self._hardware_settings)

  @property
  def settings_directory(self):
    settings_dir = self._hardware_settings_dir
    if settings_dir:
      return settings_dir
    # default to using a locally saved settings file (if present)
    local_file = os.path.join(os.getcwd(), UARM_HARDWARE_SETTINGS_FILE_NAME)
    if os.path.isfile(local_file):
      return os.getcwd()
    # fallback to using pre-defined folder for storing hardware settings
    # TODO: change to an OS-defined user-data folder
    settings_dir = os.path.dirname(os.path.realpath(__file__))
    settings_dir = os.path.join(
      settings_dir, '..', UARM_HARDWARE_SETTINGS_DIRECTORY)
    return os.path.abspath(settings_dir)

  def set_settings_directory(self, directory=None):
    if directory is None:
      return
    if not os.path.isdir(directory):
      raise ValueError('Directory does not exist: {0}'.format(directory))
    self._hardware_settings_dir = os.path.abspath(directory)

  @property
  def hardware_settings_path(self):
    return os.path.join(
      self.settings_directory, UARM_HARDWARE_SETTINGS_FILE_NAME)

  @property
  def recordings_path(self):
    return os.path.join(
      self.settings_directory, UARM_HARDWARE_RECORDINGS_FILE_NAME)

  def hardware_settings_default(self):
    self._hardware_settings = copy.deepcopy(UARM_DEFAULT_HARDWARE_SETTINGS)
    return self

  def _init_hardware_settings_file(self):
    file_path = self.hardware_settings_path
    if not os.path.isdir(os.path.dirname(file_path)):
      os.mkdir(os.path.dirname(file_path))
    if not os.path.isfile(file_path):
      init_data = {'simulate': UARM_DEFAULT_HARDWARE_SETTINGS}
      if self._hardware_settings['id'] != 'simulate':
        init_data[self._hardware_settings['id']] = self._hardware_settings
      settings_json = json.dumps(init_data, indent=4)
      with open(file_path, 'w') as f:
        f.write(settings_json)
    return self

  def _read_hardware_settings(self, file_path):
    read_data = None
    with open(file_path, 'r') as f:
      read_data = f.read()
    try:
      read_data = json.loads(read_data)
    except:
      read_data = copy.deepcopy(UARM_DEFAULT_HARDWARE_SETTINGS)
    return read_data

  def save_hardware_settings(self, **kwargs):
    for key, value in kwargs.items():
      if key in self._hardware_settings:
        self._hardware_settings[key] = value
    self._init_hardware_settings_file()
    file_path = self.hardware_settings_path
    read_data = self._read_hardware_settings(file_path)
    read_data[self._hardware_settings['id']] = self.hardware_settings
    write_data = json.dumps(read_data, indent=4)
    with open(file_path, 'w') as f:
      f.write(write_data)
    return self

  def _init_settings(self):
    self._init_hardware_settings_file()
    file_path = self.hardware_settings_path
    read_data = self._read_hardware_settings(file_path)
    current_id = self._hardware_settings['id']
    self._hardware_settings = read_data.get(
      current_id, copy.deepcopy(UARM_DEFAULT_HARDWARE_SETTINGS))
    self._hardware_settings['id'] = current_id
    for key, item in UARM_DEFAULT_HARDWARE_SETTINGS.items():
      if key not in self._hardware_settings:
        self._hardware_settings[key] = copy.deepcopy(item)
    self._recorder = Recorder(self.recordings_path)
    return self

  '''
  ATOMIC COMMANDS
  '''

  def can_move_to(self, x=None, y=None, z=None):
    logger.debug('can_move_to: x={0}, y={1}, z={2}'.format(x, y, z))
    if self.is_simulating():
      return True  # no way to test during simulation
    new_pos = self._pos.copy()
    if x is not None:
      new_pos['x'] = x
    if y is not None:
      new_pos['y'] = y
    if z is not None:
      new_pos['z'] = z
    new_pos = round_position(new_pos)
    # Send coordinates to uArm to see if they are within the limit.
    # This must be done on the device itself, because of it's weird
    # coordinate system and load-carrying ability at different positions.
    new_pos = self._remove_z_offset(new_pos)
    unreachable = self.check_pos_is_limit(list(new_pos.values()))
    return not bool(unreachable)

  def can_move_relative(self, x=None, y=None, z=None):
    logger.debug('can_move_relative: x={0}, y={1}, z={2}'.format(x, y, z))
    new_pos = self._pos.copy()
    if x is not None:
      new_pos['x'] = x + new_pos['x']
    if y is not None:
      new_pos['y'] = y + new_pos['y']
    if z is not None:
      new_pos['z'] = z + new_pos['z']
    new_pos = round_position(new_pos)
    return self.can_move_to(**new_pos)

  def move_to(self, x=None, y=None, z=None, check=False, translate=True):
    """
    Move to an absolute cartesian coordinate
    :param x: Cartesian millimeter of the X axis, if None then uses current position
    :param y: Cartesian millimeter of the Y axis, if None then uses current position
    :param z: Cartesian millimeter of the Z axis, if None then uses current position
    :param check: If True, asks the connected uArm device if the target coordinate is within its range of movement
    :return: self
    """
    logger.debug('move_to: x={0}, y={1}, z={2}'.format(x, y, z))
    if not self._enabled:
      self.enable_all_motors()
    new_pos = self._pos.copy()
    if x is not None:
      new_pos['x'] = x
    if y is not None:
      new_pos['y'] = y
    if z is not None:
      new_pos['z'] = z
    new_pos = round_position(new_pos)
    if translate:
      real_pos = self._remove_z_offset(new_pos)
    else:
      real_pos = new_pos.copy()
    if not self.is_simulating():
      if check and not self.can_move_to(**real_pos):
        raise RuntimeError(
          'Coordinate not reachable by uArm: {0}'.format(new_pos))
      speed_mm_per_min = self._speed * 60
      self.set_position(relative=False, speed=speed_mm_per_min, **real_pos)

    self._pos = new_pos.copy()
    return self

  def _set_z_offset(self, z_offset=0):
    real_z = self.position['z'] + self.hardware_settings['z_offset']
    self.save_hardware_settings(z_offset=z_offset)
    self._pos['z'] = real_z - self.hardware_settings['z_offset']
    return self

  def z_offset_reset(self):
    self._set_wrist_offset(wrist_offset=0)
    return self

  def z_is_level(self):
    self.update_position()
    real_z = self.position['z'] + self.hardware_settings['z_offset']
    z_offset = -real_z
    self._set_z_offset(z_offset=z_offset)
    return self

  def move_relative(self, x=None, y=None, z=None, check=False):
    """
    Move to a relative cartesian coordinate, away from it's current coordinate
    :param x: Cartesian millimeter of the X axis, if None then uses current position
    :param y: Cartesian millimeter of the Y axis, if None then uses current position
    :param z: Cartesian millimeter of the Z axis, if None then uses current position
    :param check: If True, asks the connected uArm device if the target coordinate is within its range of movement
    :return: self
    """
    logger.debug('move_relative: x={0}, y={1}, z={2}'.format(x, y, z))
    rel_pos = self._pos.copy()
    if x is not None:
      rel_pos['x'] = x + self._pos['x']
    if y is not None:
      rel_pos['y'] = y + self._pos['y']
    if z is not None:
      rel_pos['z'] = z + self._pos['z']
    rel_pos = round_position(rel_pos)
    # using only absolute movements, because accelerations do not seem to take
    # affect when using relative movements (not sure if firmware or API issue)
    self.move_to(check=check, **rel_pos)
    return self

  def rotate_to(self, angle=UARM_DEFAULT_WRIST_ANGLE,
                sleep=UARM_DEFAULT_WRIST_SLEEP, wait=True, translate=True):
    """
    Rotate the wrist's servo motor to a angle, in degrees
    :param angle: The target servo angle in degrees, 90 is center
    :param sleep: The number of seconds to wait after setting the angle, default is 0.25 seconds
    :param wait: If True, will wait for the connected uArm device to finish processing the command
    :return: self
    """
    logger.debug('rotate_to')
    if angle < UARM_MIN_WRIST_ANGLE:
      angle = UARM_MIN_WRIST_ANGLE
      logger.debug('angle changed to: {0}'.format(angle))
    if angle > UARM_MAX_WRIST_ANGLE:
      angle = UARM_MAX_WRIST_ANGLE
      logger.debug('angle changed to: {0}'.format(angle))
    # previous move command will return before it has arrived at destination
    if wait:
      self.wait_for_arrival(check=False)
    # speed has no affect, b/c servo motors are controlled by PWM
    # so from the device's perspective, the change is instantaneous
    if not self.is_simulating():
      if translate:
        real_angle = angle + self.hardware_settings['wrist_offset']
      else:
        real_angle = angle
      self.set_wrist(angle=real_angle)
      time.sleep(sleep)
    self._wrist_angle = angle
    return self

  def rotate_relative(self, angle=0, sleep=UARM_DEFAULT_WRIST_SLEEP,
                      wait=True):
    """
    Rotate the wrist's servo motor by a relative angle, in degrees
    :param angle: The relative amount to rotate the servo angle in degrees
    :param sleep: The number of seconds to wait after setting the angle, default is 0.25 seconds
    :param wait: If True, will wait for the connected uArm device to finish processing the command
    :return: self
    """
    logger.debug('rotate_relative')
    angle = self._wrist_angle + angle
    self.rotate_to(angle=angle, sleep=sleep, wait=wait)
    return self

  def disable_base(self):
    """
    Turn off the connected uArm's base stepper motor
    :return: self
    """
    logger.debug('disable_base')
    if not self.is_simulating():
      self.set_servo_detach(UARM_MOTOR_IDS['base'], wait=True)
    self._enabled = False
    return self

  def disable_all_motors(self):
    """
    Turn off all the connected uArm's stepper motors
    :return: self
    """
    logger.debug('disable_all_motors')
    if not self.is_simulating():
      self.set_servo_detach(None, wait=True)
    self._enabled = False
    return self

  def enable_all_motors(self):
    """
    Turn on all the connected uArm's stepper motors
    :return: self
    """
    logger.debug('enable_all_motors')
    if not self.is_simulating():
      self.set_servo_attach(None, wait=True)
    self._enabled = True
    # update position, b/c no way to know where we are
    self.update_position()
    return self

  def pump(self, enable=False, sleep=None):
    """
    Turn on all the connected uArm's stepper motors
    :param enable: If True the pump turns on, else if False the pump turns off
    :param sleep: (optional) number of seconds to wait after the sending the command, default is 0.2 seconds
    :return: self
    """
    logger.debug('pump: {0}'.format(enable))
    if self.hardware_settings['mode'] != 'general':
      raise RuntimeError(
        'Must be in \"general\" to user pump')
    if self.is_simulating():
      return self
    ret = self.set_pump(enable)
    if sleep is None:
      sleep = UARM_DEFAULT_PUMP_SLEEP[enable]
    time.sleep(sleep)
    return self

  def grip(self, enable=False, sleep=None):
    """
    Turn on all the connected uArm's stepper motors
    :param enable: If True the gripper turns on, else if False the gripper turns off
    :param sleep: (optional) number of seconds to wait after the sending the command, default is 2 seconds
    :return: self
    """
    logger.debug('grip: {0}'.format(enable))
    if self.hardware_settings['mode'] != 'pen_gripper':
      raise RuntimeError(
        'Must be in \"pen_gripper\" to user gripper')
    if self.is_simulating():
      return self
    ret = self.set_gripper(enable)
    if sleep is None:
      sleep = UARM_DEFAULT_GRIP_SLEEP[enable]
    time.sleep(sleep)
    return self

  def is_gripping(self):
    if self.is_simulating():
      return False
    return bool(self.get_gripper_catch() > 0)

  def is_pumping(self):
    if self.is_simulating():
      return False
    return bool(self.get_pump_status() > 0)

  def is_pressing(self):
    """
    Check to see if the pump's limit switch is being pressed
    :return: True if the switch is pressed, else False
    """
    logger.debug('is_pressing')
    if self.hardware_settings['mode'] != 'general':
      raise RuntimeError(
        'Must be in \"general\" mode to test if pressing something')
    if self.is_simulating():
      raise RuntimeError('Not able to read limit switching while simulating')
    return self.get_limit_switch(wait=True)

  '''
  COMBINATORY COMMANDS
  '''

  def home(self):
    """
    Reset the connected uArm device, and move it to a safe position, one axis at a time
    :return: self
    """
    logger.debug('home')
    self.push_settings()
    self.speed(UARM_HOME_SPEED)
    self.acceleration(UARM_HOME_ACCELERATION)
    # move to a know absolute position first, or else the follow
    # servo-angle commands will act unpredictably
    self.move_to(translate=False, **UARM_HOME_START_POS)
    self.wait_for_arrival(check=False)
    # move to the "safe" position, where it is safe to disable all motors
    # using angles ensures it's the same regardless of mode (coordinate system)
    if self.is_simulating():
      self.move_to(translate=False, **UARM_HOME_SIMULATE_POS)
    else:
      for m_id in UARM_HOME_ORDER:
        self.set_servo_angle(
          servo_id=m_id, angle=UARM_HOME_ANGLE[m_id], wait=True)
    self.wait_for_arrival(check=False)
    self.pop_settings()
    # b/c using servo angles, Python has lost track of where XYZ are
    if not self.is_simulating():
      time.sleep(0.25) # give it an extra time to ensure position is settled
    self.update_position()
    self.rotate_to(UARM_DEFAULT_WRIST_ANGLE)
    return self

  def probe(self, step=UARM_DEFAULT_PROBE_STEP, speed=UARM_DEFAULT_PROBE_SPEED):
    """
    Move the connected uArm device down until the pump's limit switch is being pressed
    :param step: number of millimeter to move before checking, default is 1 millimeter
    :param speed: speed to move while probing, default is 10mm/sec
    :return: self
    """
    # TODO: see if `register_limit_switch_callback()` can be used to halt
    logger.debug('probe')
    self.push_settings()
    self.speed(speed)
    # move down until we hit the limit switch
    while not self.is_simulating() and not self.is_pressing():
      self.move_relative(z=-step).wait_for_arrival()
    self.pop_settings()
    return self

  def sleep(self):
    """
    Home the connected uArm device, and then disable all motors
    :return: self
    """
    if self.hardware_settings['mode'] == 'general':
      self.pump(False, sleep=0)
    elif self.hardware_settings['mode'] == 'pen_gripper':
      self.grip(False, sleep=0)
    self.home().disable_all_motors()

  def wait_for_touch(self, distance=None, timeout=None):
    """
    Monitor the position of all motors to detect if the uArm has been touched, potentially moving one of the axes slightly
    :param distance: number of millimeter to move to trigger a touch event, default is 0.25 millimeters
    :param timeout: number of seconds to wait for a touch event, default is forever
    :return: self
    """
    if self.is_simulating():
      # just don't even bother if simulating, return immediately
      return self
    self.wait_for_arrival(check=False)
    start_time = time.time()
    self.update_position()
    if distance is None:
      distance = UARM_DEFAULT_TOUCH_THRESH_MM
    start_pos = self.position
    while True:
      if timeout and time.time() - start_time > timeout:
        raise RuntimeError(
          'uArm timed out waiting for a touch ({0} seconds)', timeout)
      self.update_position()
      moved, _, _ = cartesian_to_polar(
        **subtract_positions(self.position, start_pos))
      if moved > distance:
        return self

  '''
  RECORD/PLAYBACK COMMANDS
  '''
  def record(self,
             name,
             overwrite=False,
             check=True,
             method=None,
             still_seconds=1,
             still_distance=1):
    self._recorder.record(self,
                          name,
                          overwrite=overwrite,
                          check=check,
                          method=method,
                          still_seconds=still_seconds,
                          still_distance=still_distance)
    return self

  def erase(self, name):
    self._recorder.erase(name)
    return self

  def playback(self, name, relative=False, speed=None, check=False):
    self._recorder.playback(
      self, name, relative=relative, speed=speed, check=check)
    return self

  def process_recording(self, name, filter=False, max_angle=None):
    self._recorder.process(name, filter=filter, max_angle=max_angle)
    return self
