from uarm.offset import get_rotated_offset_at_angle
from uarm.offset import get_position_for_offset_target_at
from uarm.offset import add_positions, cartesian_to_polar
from uarm.offset import get_openmv_offset


def get_openmv_position(uarm_position,
                        uarm_angle=None,
                        mode='general',
                        openmv_offset=None):
  if uarm_angle is None:
    # Note: this only works because all uArm modes have a Y offset of 0.0
    _, uarm_angle, _ = cartesian_to_polar(**uarm_position)
  if openmv_offset is None:
    openmv_offset = get_openmv_offset(mode=mode)
  real_openmv_offset = get_rotated_offset_at_angle(uarm_angle, openmv_offset)
  return add_positions(uarm_position, real_openmv_offset)


def get_position_from_image_offset(image_offset,
                                   uarm_position,
                                   uarm_angle=None,
                                   mode='general',
                                   openmv_offset=None):
  # TODO: system for converting pixels to millimeters
  rotated_image_offset = get_rotated_offset_at_angle(uarm_angle, image_offset)
  openmv_position = get_openmv_position(
    mode, uarm_position, uarm_angle=uarm_angle, openmv_offset=openmv_offset)
  return add_positions(openmv_position, rotated_image_offset)


def get_position_for_openmv_at(target, mode='general', openmv_offset=None):
  if openmv_offset is None:
    openmv_offset = get_openmv_offset(mode=mode)
  return get_position_for_offset_target_at(target, openmv_offset)


if __name__ == '__main__':
  uarm_pos = {'x': 0, 'y': 100, 'z': 0}
  print(get_openmv_offset(mode='general'))
  print(get_openmv_position(uarm_pos))
  print(get_openmv_offset(mode='laser'))
  print(get_openmv_position(uarm_pos, mode='laser'))
