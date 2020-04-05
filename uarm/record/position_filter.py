import logging
import math

logger = logging.getLogger('uarm.swiftapi.record')


UARM_TRAIN_ANGLE_FILTER_DEFAULT = math.pi / 16


def get_distance(pos1, pos2):
  diff = {
    ax: pos2[ax] - pos1[ax]
    for ax in 'xyz'
  }
  return math.sqrt(sum([
    math.pow(diff[ax], 2) for ax in 'xyz'
  ]))


def get_sphere_coords(pos1, pos2):
  diff = {
    ax: pos2[ax] - pos1[ax]
    for ax in 'xyz'
  }
  dist = get_distance(pos1, pos2)
  theta = 0
  if diff['x'] != 0:
    theta = math.atan(diff['y'] / diff['x'])
  else:
    theta = math.pi * 0.5
    if diff['y'] < 0:
      theta += math.pi
  phi  = 0
  if dist != 0:
    phi = math.acos(diff['z'] / dist)
  return (dist, theta, phi)


def get_abs_radian_diff(rad_1, rad_2):
  abs_diff = abs(rad_2 - rad_1)
  if abs_diff > math.pi:
    abs_diff = (2 * math.pi) - abs_diff
  return abs_diff


def did_move_too_much(prev_sphere, new_sphere, max_angle):
  distance = new_sphere[0]
  if distance == 0:
    return False
  abs_diff_radians = [
    get_abs_radian_diff(prev_sphere[i], new_sphere[i])
    for i in (1, 2)
  ]
  for rad in abs_diff_radians:
    if rad > max_angle:
      return True
  return False


def filter_absolute_data(samples, max_angle=UARM_TRAIN_ANGLE_FILTER_DEFAULT):
  if not isinstance(max_angle, float):
    max_angle = UARM_TRAIN_ANGLE_FILTER_DEFAULT
  trimmed_data = samples[:1]
  prev_sphere = get_sphere_coords(
    trimmed_data[-1]['position'], samples[1]['position'])
  for i in range(2, len(samples)):
    new_sphere = get_sphere_coords(
      trimmed_data[-1]['position'], samples[i]['position']
    )
    moved = did_move_too_much(prev_sphere, new_sphere, max_angle)
    if moved:
      trimmed_data.append(samples[i - 1])
      prev_sphere = get_sphere_coords(
        trimmed_data[-1]['position'], samples[i]['position']
      )
  trimmed_data.append(samples[-1])
  return trimmed_data
