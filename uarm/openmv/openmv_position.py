from .position_offsets import get_rotated_offset_at_angle
from .position_offsets import get_position_for_offset_target
from .position_offsets import add_positions

# OPENMV CAMERA OFFSET
UARM_OPENMV_OFFSET = {'x': 62, 'y': 10, 'z': 30}

# TODO: system for converting pixels to millimeters


def get_openmv_position(position, angle, openmv_offset=UARM_OPENMV_OFFSET):
  real_openmv_offset = get_rotated_offset_at_angle(angle, openmv_offset)
  return add_positions(position, real_openmv_offset)


def get_image_position(position,
                       angle,
                       img_offset,
                       openmv_offset=UARM_OPENMV_OFFSET):
  real_img_offset = get_rotated_offset_at_angle(angle, img_offset)
  real_openmv_offset = get_rotated_offset_at_angle(angle, openmv_offset)
  return add_positions(position, real_openmv_offset, real_img_offset)


def get_position_for_openmv(target, offset=UARM_OPENMV_OFFSET):
  return get_position_for_offset_target(target, offset)
