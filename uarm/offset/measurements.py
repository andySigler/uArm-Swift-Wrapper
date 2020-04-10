UARM_MODE_OFFSETS = {
  'general': {'x': 0.0, 'y': 0.0, 'z': 0.0},  # global reference point
  'laser': {'x': 7.75, 'y': 0.0, 'z': 23.51},
  '3d_printer': {'x': -0.15, 'y': 0.0, 'z': 0.12},
  'pen_gripper': {'x': 12.85, 'y': 0.0, 'z': 31.55}
}

UARM_PUMP_SIZE = {'x': 20, 'y': 20, 'z': 39.7}
UARM_PUMP_GENERAL_OFFSET = {'x': 0, 'y': 0, 'z': 0}

UARM_SERVO_SIZE = {'x': 34.7, 'y': 19, 'z': 0}
UARM_SERVO_GENERAL_OFFSET = {
  'x': -11.85, 'y': -UARM_SERVO_SIZE['y'] / 2, 'z': UARM_PUMP_SIZE['z']
}

UARM_OPENMV_MOUNT_THICKNESS = {'x': 2, 'y': 2}
UARM_OPENMV_MOUNT_GENERAL_OFFSET = {
  'x': UARM_SERVO_GENERAL_OFFSET['x'] + UARM_SERVO_SIZE['x'],
  'y': UARM_SERVO_GENERAL_OFFSET['y'],
  'z': 24 + UARM_SERVO_GENERAL_OFFSET['z']  # the flat top
}

UARM_OPENMV_SIZE = {'x': 54.6, 'y': 44.5, 'z': 26.5}  # flat top, lense bottom
UARM_OPENMV_LENSE = {'x': 44.5, 'y': UARM_OPENMV_SIZE['y'] / 2, 'z': 0}
UARM_OPENMV_GENERAL_OFFSET = {
  'x': UARM_OPENMV_MOUNT_GENERAL_OFFSET['x'] + UARM_OPENMV_MOUNT_THICKNESS['x'] + UARM_OPENMV_LENSE['x'],
  'y': UARM_OPENMV_MOUNT_GENERAL_OFFSET['y'] + UARM_OPENMV_MOUNT_THICKNESS['y'] + UARM_OPENMV_LENSE['y'],
  'z': UARM_OPENMV_MOUNT_GENERAL_OFFSET['z'] - UARM_OPENMV_SIZE['z']
}


def _get_offset_in_mode(mode, offset):
  if mode not in UARM_MODE_OFFSETS.keys():
    raise ValueError('Unknown uArm mode: {0}'.format(mode))
  return {ax: offset[ax] - UARM_MODE_OFFSETS[mode][ax] for ax in 'xyz'}


def get_pump_offset(mode='general'):
  return _get_offset_in_mode(mode, UARM_PUMP_GENERAL_OFFSET)


def get_openmv_offset(mode='general'):
  return _get_offset_in_mode(mode, UARM_OPENMV_GENERAL_OFFSET)

