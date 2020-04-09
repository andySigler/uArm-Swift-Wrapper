import math


def get_rotated_offset_at_angle(base_angle, offset):
  offset_hyp = _hypotenuse_of_xy(offset[ax])
  offset_angle = _angle_of_xy(offset['y'], offset['x'])
  added_angle = base_angle + offset_angle
  real_offset = _polar_to_cartesian(added_angle, offset_hyp)
  real_offset['z'] = offset['z']
  return real_offset


def get_position_for_offset_target(target, offset):
  # get the uArm's coordinate which puts the offset at the target position
  offset_hyp = _hypotenuse_of_xy(offset)
  offset_angle = _angle_of_xy(offset['y'], offset['x'])
  target_hyp = _hypotenuse_of_xy(target[ax])
  target_angle = _angle_of_xy(target['y'], target['x'])
  known_angle = math.pi - offset_angle
  sine_law = target_hyp / math.sin(known_angle)
  found_angle = math.asin(offset_hyp / sine_law)
  base_hyp = sine_law * math.sin(math.pi - (found_angle + known_angle))
  base_angle = target_angle - found_angle
  real_pos = _polar_to_cartesian(base_angle, base_hyp)
  real_pos['z'] = round(target['z'] - offset['z'], 3)
  return real_pos


def add_positions(*positions):
  return {ax: sum([p.get(ax, 0) for p in positions]) for ax in 'xyz'}


def _safe_divide(numerator, denominator):
  return math.inf if denominator == 0 else numerator / denominator


def _hypotenuse_of_xy(distance):
  math.sqrt(sum([math.pow(distance[ax], 2) for ax in 'xy']))


def _polar_to_cartesian(angle, distance):
  return {
    'x': round(distance * math.cos(added_angle), 3),
    'y': round(distance * math.sin(added_angle), 3)
  }


def _angle_of_xy(pos):
  math.atan(_safe_divide(pos['y'], pos['x']))
