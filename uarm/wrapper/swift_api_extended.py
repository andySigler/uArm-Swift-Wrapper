import math
import time

from serial.tools.list_ports import comports
from . import SwiftAPI


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
  # 'laser': 1,
  # '3d_printer': 2,
  'pen_gripper': 3
}
UARM_CODE_TO_MODE = {
  val: key
  for key, val in UARM_MODE_TO_CODE.items()
}

UARM_MOTOR_IDS = {
  'base': 0,
  'shoulder': 1,
  'elbow': 2,
  'wrist': 3
}

# MIN/MAX POSITIONS (are these useful?)
UARM_POSITION_MIN = {
  'x': 110,
  'y': -350,
  'z': -100 # not sure what this should be exactly
}
UARM_POSITION_MAX = {
  'x': 330,
  'y': 350,
  'z': 150
}

# SPEED
UARM_DEFAULT_SPEED_FACTOR = 0.007
UARM_MAX_SPEED = 600
UARM_MIN_SPEED = 1
UARM_DEFAULT_SPEED = 150

# ACCELERATION
UARM_MAX_ACCELERATION = 50
UARM_MIN_ACCELERATION = 0.01
UARM_DEFAULT_ACCELERATION = 5

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


def _is_uarm_port(port_info):
  return (port_info.hwid and UARM_USB_HWID in port_info.hwid)


def _serial_print_port_info(port_info):
  print('- Port: {0}'.format(port_info.device))
  for key, val in port_info.__dict__.items():
    if (key != 'device' and val and val != 'n/a'):
      print('\t- {0}: {1}'.format(key, val))


def _get_uarm_ports(verbose=False):
  found_ports = []
  for p in comports():
    if verbose:
      _serial_print_port_info(p)
    if _is_uarm_port(p):
      found_ports.append(p)
  return found_ports


def uarm_create(verbose=False, verbose_serial=False, **kwargs):
  return SwiftAPIExtended(verbose=verbose, verbose_serial=verbose_serial, **kwargs)


def uarm_scan(verbose=False, verbose_serial=False, **kwargs):
  found_swifts = []
  for port_info in _get_uarm_ports(verbose=verbose):
    try:
      swift = uarm_create(
          port=port_info.device,
          verbose=verbose,
          verbose_serial=verbose_serial,
          **kwargs)
      found_swifts.append(swift)
    except Exception as e:
      print(e)
  if len(found_swifts):
    return found_swifts
  raise RuntimeError('Unable to find uArm ports')


def uarm_scan_and_connect(verbose=False, verbose_serial=False, **kwargs):
  c_swift = None
  for swift in uarm_scan(verbose=verbose, verbose_serial=verbose_serial, **kwargs):
    try:
      swift.connect()
      c_swift = swift
      break
    except Exception as e:
      print(e)
      continue
  if c_swift:
    if verbose:
      print('Connected to uArm on port: {0}'.format(c_swift.port))
      for key, val in c_swift.get_device_info().items():
        print('\t- {0}: {1}'.format(key, val))
    return c_swift
  raise RuntimeError('Unable to find uArm port')


class SwiftAPIExtended(SwiftAPI):

  def __init__(self, connect=False, simulate=False, **kwargs):

    '''
    connect: during instantiation, should connect to serial port
    simulate: makes this class intance unable to connect, only simulates

    '''

    self._enabled = False  # safer to assume motors are disabled
    self._simulating = simulate
    self._port = kwargs.get('port', 'unknown')

    # run self.update_position() to get real position from uArm
    self._pos = UARM_HOME_SIMULATE_POS.copy()
    self._wrist_angle = UARM_DEFAULT_WRIST_ANGLE

    self._mode_str = UARM_DEFAULT_MODE
    self._mode_code = UARM_MODE_TO_CODE[self._mode_str]
    self._speed = UARM_DEFAULT_SPEED
    self._acceleration = UARM_DEFAULT_ACCELERATION
    self._pushed_speed = []
    self._pushed_acceleration = []

    super().__init__(do_not_open=True, **kwargs)
    if connect:
      self.connect()
    elif simulate:
      self.setup()

  def _log_verbose(self, msg):
    if self._verbose:
      print(msg)

  '''
  SETTINGS, UTILS, and MODES
  '''

  @property
  def port(self):
    return self._port

  def connect(self, *args, **kwargs):
    self._log_verbose('connect')
    if self.is_simulating():
      raise RuntimeError(
        'uArm is in \"simulate\" mode, cannot connect to device')
    super().connect(*args, **kwargs)
    self.waiting_ready(timeout=3)
    if kwargs.get('port'):
      self._port = kwargs.get('port')
    self.test_device_info()
    self.setup()

  def disconnect(self, *args, **kwargs):
    self._log_verbose('disconnect')
    if self.is_simulating():
      raise RuntimeError(
        'uArm is in \"simulate\" mode, cannot disconnect from device')
    super().disconnect(*args, **kwargs)

  def is_simulating(self):
    return bool(self._simulating)

  def test_device_info(self):
    self._log_verbose('test_device_info')
    if self.is_simulating():
      raise RuntimeError(
        'uArm is in \"simulate\" mode, cannot test device info')
    info = self.get_device_info()
    self._log_verbose(info)
    dt = info.get('device_type')
    if not dt or dt != UARM_DEVICE_TYPE:
      raise RuntimeError('Device type should be {0}, but got {1}'.format(
        UARM_DEVICE_TYPE, dt))
    fw = info.get('firmware_version')
    if not fw or fw not in UARM_ALLOWED_FIRMWARE_VERSIONS:
      raise RuntimeError('Device FW version {0} not within {1}'.format(
        fw, UARM_ALLOWED_FIRMWARE_VERSIONS))

  def setup(self):
    self._log_verbose('setup')
    if not self.is_simulating():
      self.flush_cmd()
      self.waiting_ready()
    self.set_speed_factor(UARM_DEFAULT_SPEED_FACTOR)
    self.mode(self._mode_str)
    return self

  def push_settings(self):
    self._pushed_speed.append(float(self._speed))
    self._pushed_acceleration.append(float(self._acceleration))
    return self

  def pop_settings(self):
    if len(self._pushed_speed) == 0 or len(self._pushed_acceleration) == 0:
      raise RuntimeError('Cannot "pop" settings when none have been "pushed"')
    self.speed(float(self._pushed_speed[-1]))
    self._pushed_speed = self._pushed_speed[:-1]
    self.acceleration(float(self._pushed_acceleration[-1]))
    self._pushed_acceleration = self._pushed_acceleration[:-1]
    return self

  def wait_for_arrival(self, timeout=10, set_pos=True):
    self._log_verbose('wait')
    if self.is_simulating():
      return self
    start_time = time.time()
    self.waiting_ready(timeout=timeout)
    while time.time() - start_time < timeout:
      # sending these commands while moving will make uArm much less smooth
      if set_pos:
        self.move_to(check=False, **self._pos)
      time.sleep(0.02)
      if not self.get_is_moving(wait=True):
        return self
    raise TimeoutError(
      'Unable to arrive within {1} seconds'.format(timeout))

  def mode(self, new_mode):
    self._log_verbose('mode: {0}'.format(new_mode))
    if new_mode not in UARM_MODE_TO_CODE.keys():
      raise ValueError('Unknown mode: {0}'.format(new_mode))
    self._mode_str = new_mode
    self._mode_code = UARM_MODE_TO_CODE[self._mode_str]
    if not self.is_simulating():
      self.set_mode(UARM_MODE_TO_CODE[self._mode_str])
    self.update_position()
    return self

  def speed(self, speed):
    self._log_verbose('speed: {0}'.format(speed))
    if speed < UARM_MIN_SPEED:
      speed = UARM_MIN_SPEED
      self._log_verbose('speed changed to: {0}'.format(speed))
    if speed > UARM_MAX_SPEED:
      speed = UARM_MAX_SPEED
      self._log_verbose('speed changed to: {0}'.format(speed))
    self._speed = speed
    return self

  def speed_percentage(self, percentage):
    self._log_verbose('speed_percentage: {0}'.format(percentage))
    if percentage < 0:
      percentage = 0
    if percentage > 100:
      percentage = 100
    speed = (UARM_MAX_SPEED - UARM_MIN_SPEED) * percentage
    speed +=  UARM_MIN_SPEED
    self.speed(speed)
    return self

  def acceleration(self, acceleration):
    self._log_verbose('acceleration: {0}'.format(acceleration))
    if acceleration < UARM_MIN_ACCELERATION:
      acceleration = UARM_MIN_ACCELERATION
      self._log_verbose('acceleration changed to: {0}'.format(acceleration))
    if acceleration > UARM_MAX_ACCELERATION:
      acceleration = UARM_MAX_ACCELERATION
      self._log_verbose('acceleration changed to: {0}'.format(acceleration))
    self._acceleration = acceleration
    if not self.is_simulating():
      self.set_acceleration(acc=self._acceleration)
    return self

  def update_position(self):
    self._log_verbose('update_position')
    if self.is_simulating():
      return self
    pos = self.get_position(wait=True)
    is_n = pos is None
    is_l = isinstance(pos, list)
    if is_n or not is_l or not len(pos) or not isinstance(pos[0], float):
      print('Not able to read position, out of bounds')
      return self
    self._pos = {
      'x': round(pos[0], 2),
      'y': round(pos[1], 2),
      'z': round(pos[2], 2)
    }
    self._log_verbose('New Position: {0}'.format(self._pos))
    return self

  @property
  def position(self):
    return self._pos.copy()

  '''
  ATOMIC COMMANDS
  '''

  def move_to(self, x=None, y=None, z=None, check=True):
    self._log_verbose('move_to: x={0}, y={1}, z={2}'.format(x, y, z))
    if not self._enabled:
      self.enable_all_motors()
    new_pos = self._pos.copy()
    if x is not None:
      new_pos['x'] = round(x, 2)
    if y is not None:
      new_pos['y'] = round(y, 2)
    if z is not None:
      new_pos['z'] = round(z, 2)
    if check:
      for ax in UARM_POSITION_MIN.keys():
        min_ax = UARM_POSITION_MIN[ax]
        max_ax = UARM_POSITION_MAX[ax]
        if new_pos[ax] <= min_ax or new_pos[ax] >= max_ax:
          raise RuntimeError(
            'Unable to reach {0} axis to position {1}'.format(
              ax.upper(), new_pos[ax]))
    speed_mm_per_min = self._speed * 60
    if not self.is_simulating():
      self.set_position(relative=False, speed=speed_mm_per_min, **new_pos)
    self._pos = new_pos
    return self

  def move_relative(self, x=None, y=None, z=None):
    self._log_verbose('move_relative: x={0}, y={1}, z={2}'.format(x, y, z))
    kwargs = {}
    if x is not None:
      kwargs['x'] = round(x + self._pos['x'], 2)
    if y is not None:
      kwargs['y'] = round(y + self._pos['y'], 2)
    if z is not None:
      kwargs['z'] = round(z + self._pos['z'], 2)
    # using only absolute movements, because accelerations do not seem to take
    # affect when using relative movements (not sure if firmware or API issue)
    self.move_to(**kwargs)
    return self

  def rotate_to(self, angle=UARM_DEFAULT_WRIST_ANGLE,
                sleep=UARM_DEFAULT_WRIST_SLEEP, wait=True):
    self._log_verbose('rotate_to')
    if angle < UARM_MIN_WRIST_ANGLE:
      angle = UARM_MIN_WRIST_ANGLE
      self._log_verbose('angle changed to: {0}'.format(angle))
    if angle > UARM_MAX_WRIST_ANGLE:
      angle = UARM_MAX_WRIST_ANGLE
      self._log_verbose('angle changed to: {0}'.format(angle))
    self._wrist_angle = angle
    # previous move command will return before it has arrived at destination
    if wait:
      self.wait_for_arrival()
    # speed has no affect, b/c servo motors are controlled by PWM
    # so from the device's perspective, the change is instantaneous
    if not self.is_simulating():
      self.set_wrist(angle=angle)
      time.sleep(sleep)
    return self

  def rotate_relative(self, angle=0, sleep=UARM_DEFAULT_WRIST_SLEEP,
                      wait=True):
    self._log_verbose('rotate_relative')
    angle = self._wrist_angle + angle
    self.rotate_to(angle=angle, sleep=sleep, wait=wait)
    return self

  def disable_base(self):
    self._log_verbose('disable_base')
    if not self.is_simulating():
      self.set_servo_detach(UARM_MOTOR_IDS['base'], wait=True)
    self._enabled = False
    return self

  def disable_all_motors(self):
    self._log_verbose('disable_all_motors')
    if not self.is_simulating():
      self.set_servo_detach(None, wait=True)
    self._enabled = False
    return self

  def enable_all_motors(self):
    self._log_verbose('enable_all_motors')
    if not self.is_simulating():
      self.set_servo_attach(None, wait=True)
    self._enabled = True
    # update position, b/c no way to know where we are
    self.update_position()
    return self

  def pump(self, enable, sleep=None):
    self._log_verbose('pump: {0}'.format(enable))
    if self._mode_str != 'general':
      raise RuntimeError(
        'Must be in \"general\" to user pump')
    if self.is_simulating():
      return self
    ret = self.set_pump(enable)
    if sleep is None:
      sleep = UARM_DEFAULT_PUMP_SLEEP[enable]
    time.sleep(sleep)
    return self

  def grip(self, enable, sleep=None):
    self._log_verbose('grip: {0}'.format(enable))
    if self._mode_str != 'pen_gripper':
      raise RuntimeError(
        'Must be in \"pen_gripper\" to user gripper')
    if self.is_simulating():
      return self
    ret = self.set_gripper(enable)
    if sleep is None:
      sleep = UARM_DEFAULT_GRIP_SLEEP[enable]
    time.sleep(sleep)
    return self

  def is_pressing(self):
    self._log_verbose('is_pressing')
    if self._mode_str != 'general':
      raise RuntimeError(
        'Must be in \"general\" mode to test if pressing something')
    if self.is_simulating():
      raise RuntimeError('Not able to read limit switching while simulating')
    return self.get_limit_switch(wait=True)

  '''
  COMBINATORY COMMANDS
  '''

  def home(self):
    self._log_verbose('home')
    self.push_settings()
    self.speed(UARM_HOME_SPEED)
    self.acceleration(UARM_HOME_ACCELERATION)
    # move to a know absolute position first, or else the follow
    # servo-angle commands will act unpredictably
    self.move_to(check=False, **UARM_HOME_START_POS).wait_for_arrival()
    self.rotate_to(UARM_DEFAULT_WRIST_ANGLE)
    # move to the "safe" position, where it is safe to disable all motors
    # using angles ensures it's the same regardless of mode (coordinate system)
    if self.is_simulating():
      self.move_to(**UARM_HOME_SIMULATE_POS)
    else:
      for m_id in UARM_HOME_ORDER:
        self.set_servo_angle(
          servo_id=m_id, angle=UARM_HOME_ANGLE[m_id], wait=True)
    self.wait_for_arrival(set_pos=False)
    self.pop_settings()
    # b/c using servo angles, Python has lost track of where XYZ are
    if not self.is_simulating():
      time.sleep(0.25) # give it an extra time to ensure position is settled
    self.update_position()
    return self

  def probe(self, step=UARM_DEFAULT_PROBE_STEP, speed=UARM_DEFAULT_PROBE_SPEED):
    self._log_verbose('probe')
    self.push_settings()
    self.speed(speed)
    # move down until we hit the limit switch
    while not self.is_pressing():
      self.move_relative(z=-step).wait_for_arrival()
    self.pop_settings()
    return self

  def sleep(self):
    if self._mode_str == 'general':
      self.pump(False, sleep=0)
    elif self._mode_str == 'pen_gripper':
      self.grip(False, sleep=0)
    self.rotate_to(angle=UARM_DEFAULT_WRIST_ANGLE, sleep=0)
    self.home().disable_all_motors()

  def wait_for_touch(self, distance=None, timeout=None):
    self.wait_for_arrival(set_pos=self._enabled)
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
      diffs = {
        ax: self.position[ax] - start_pos[ax]
        for ax in 'xyz'
      }
      sums = sum([math.pow(v, 2) for v in diffs.values()])
      moved = math.sqrt(sums)
      if moved > distance:
        return self
