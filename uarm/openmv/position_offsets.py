import math


def get_rotated_offset_at_angle(base_angle, offset):
  offset_hyp = math.sqrt(sum([
    math.pow(offset[ax], 2) for ax in 'xy'
  ]))
  offset_angle = math.atan(
    0 if offset['x'] == 0 else offset['y'] / offset['x'])
  added_angle = base_angle + offset_angle
  real_offset = offset.copy()
  real_offset['x'] = round(math.cos(added_angle) * offset_hyp, 2)
  real_offset['y'] = round(math.sin(added_angle) * offset_hyp, 2)
  return real_offset


def get_position_for_offset_target(target, offset):
  # get the uArm's coordinate which puts the offset at the target position
  offset_hyp = math.sqrt(sum([math.pow(offset[ax], 2) for ax in 'xy']))
  offset_angle = math.atan(
    0 if offset['x'] == 0 else offset['y'] / offset['x'])
  target_hyp = math.sqrt(sum([math.pow(target[ax], 2) for ax in 'xy']))
  target_angle = math.atan(
    0 if target['x'] == 0 else target['y'] / target['x'])
  known_angle = math.pi - offset_angle
  sine_law = target_hyp / math.sin(known_angle)
  found_angle = math.asin(offset_hyp / sine_law)
  base_hyp = sine_law * math.sin(math.pi - (found_angle + known_angle))
  base_angle = target_angle - found_angle
  return {
    'x': round(base_hyp * math.cos(base_angle), 3),
    'y': round(base_hyp * math.sin(base_angle), 3),
    'z': round(target['z'] - offset['z'], 3)
  }


def add_positions(*positions):
  return {ax: sum([p.get(ax, 0) for p in positions]) for ax in 'xyz'}

