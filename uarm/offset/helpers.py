import math


def get_rotated_offset_at_angle(base_angle, offset):
  '''
  Get the new cartesian offset, when the uArm's base is at an angle
  '''
  distance, angle, _ = cartesian_to_polar(**offset)
  x, y, _ = polar_to_cartesian(distance, base_angle + angle)
  return {'x': x, 'y': y, 'z': offset['z']}


def get_position_for_offset_target_at(target, offset):
  '''
  Get the uArm's coordinate, which puts the offset at the target position
  '''
  # get known angles/distances (target and offset)
  offset_distance, offset_angle, _ = cartesian_to_polar(**offset)
  target_distance, target_angle, _ = cartesian_to_polar(**target)
  # find the missing angle (b/w offset, target, and uArm's base)
  known_angle = math.pi - offset_angle
  sine_law = target_distance / math.sin(known_angle)
  found_angle = math.asin(offset_distance / sine_law)
  # find the uArm's actual base angle, and it's distance from origin
  base_distance = sine_law * math.sin(math.pi - (found_angle + known_angle))
  base_angle = target_angle - found_angle
  # get coordinates
  x, y, _ = polar_to_cartesian(base_distance, base_angle)
  return {'x': x, 'y': y, 'z': target['z'] - offset['z']}


def cartesian_to_polar(x, y, z=None):
  distance = _distance_to(x, y)
  angle = _angle_to(x, y)
  return (distance, angle, z)


def polar_to_cartesian(distance, angle, z=None):
  x = distance * math.cos(angle)
  y = distance * math.sin(angle)
  return (x, y, z)


def add_positions(*positions):
  '''
  Add two XYZ positions together
  '''
  return {ax: sum([p.get(ax, 0) for p in positions]) for ax in 'xyz'}


def _safe_divide(value, by=1):
  return math.inf if by == 0 else value / by


def _distance_to(*args):
  return math.sqrt(sum([math.pow(v, 2) for v in args]))


def _angle_to(x, y):
  return math.atan(_safe_divide(y, by=x))


def _round(position, decimal=3):
  return {
    k: round(v, decimal)
    for k, v in position.items()
  }


if __name__ == '__main__':
  offset = {'x': 10, 'y': 10, 'z': 0}

  print('\nTest get rotated offset at angle:')
  for angle in [0, math.pi * 0.25, math.pi * 0.5, math.pi]:
    print('Angle:', round(angle, 3), '({0} deg)'.format((angle / math.pi) * 180))
    new_offset = get_rotated_offset_at_angle(angle, offset)
    print(_round(new_offset))

  print('\nTest get position for offset target:')
  import random
  for _ in range(3):
    uarm_pos = {
      'x': random.randint(100, 220),
      'y': random.randint(-250, 250),
      'z': random.randint(0, 150)
    }
    _, u_angle, _ = cartesian_to_polar(**uarm_pos)
    u_offset = get_rotated_offset_at_angle(u_angle, offset)
    target = add_positions(uarm_pos, u_offset)
    u_target = get_position_for_offset_target_at(target, offset)
    print(uarm_pos, '==', _round(u_target))
