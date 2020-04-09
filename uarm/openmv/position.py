from uarm.offset import get_rotated_offset_at_angle
from uarm.offset import get_position_for_offset_target
from uarm.offset import add_positions
from uarm.offset import get_openmv_offset

# TODO: system for converting pixels to millimeters


def get_openmv_position(mode,
                        position,
                        angle,
                        openmv_offset=None):
  if openmv_offset is None:
    openmv_offset = get_openmv_offset(mode)
  real_openmv_offset = get_rotated_offset_at_angle(angle, openmv_offset)
  return add_positions(position, real_openmv_offset)


def get_image_position(mode,
                       position,
                       angle,
                       img_offset,
                       openmv_offset=None):
  if openmv_offset is None:
    openmv_offset = get_openmv_offset(mode)
  real_img_offset = get_rotated_offset_at_angle(angle, img_offset)
  real_openmv_offset = get_rotated_offset_at_angle(angle, openmv_offset)
  return add_positions(position, real_openmv_offset, real_img_offset)


def get_position_for_openmv(mode, target, openmv_offset=None):
  if openmv_offset is None:
    openmv_offset = get_openmv_offset(mode)
  return get_position_for_offset_target(target, openmv_offset)
