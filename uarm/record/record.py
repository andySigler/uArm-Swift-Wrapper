import copy
import json
import logging
import os
import time

from uarm.record.position_filter import get_distance, filter_absolute_data

logger = logging.getLogger('uarm.swiftapi.record')


UARM_TRAIN_POSITION_SAMPLE = {
  'time': 0,
  'position': {
    'x': 0,
    'y': 0,
    'z': 0
  }
}

UARM_TRAIN_SAVED_DATA = {
  'samples': [],
  'time': {
    'start': 0,
    'end': 0,
    'duration': 0
  },
  'hardware_settings': {}
}


class Recorder(object):

  def __init__(self, file_path=None):
    file_dir = os.path.dirname(file_path)
    if not os.path.isdir(file_dir):
      raise ValueError('Not a directory: {0}'.format(file_dir))
    if not os.path.isfile(file_path):
      with open(file_path, 'w') as f:
        f.write('{}\n')
    self._file_path = file_path
    self._data = {}
    self._processed_data = {}
    self._load_data()
    for name in self._data.keys():
      self.process(name, filter=False)

  def _load_data(self):
    with open(self._file_path, 'r') as f:
      data_str = f.read()
    try:
      self._data = json.loads(data_str)
    except json.decoder.JSONDecodeError as e:
      logger.exception('Exception while loading JSON record data:')

  def _save_data(self):
    data_json = json.dumps(self._data, indent=4)
    with open(self._file_path, 'w') as f:
      f.write(data_json)

  def record(self,
             robot,
             name,
             overwrite=False,
             check=True,
             method=None,
             still_seconds=1,
             still_distance=1):
    '''
    Wait for user-touch, then start recording positions
    If the robot is still, then stop recording
    '''
    if name in self._data and not overwrite:
      raise RuntimeError(
        'Recording {0} already exists, use overwrite=True'.format(name))

    _recorded_poses = []
    _test_poses = []
    _start_time = None

    def _add_position(coord):
      nonlocal _recorded_poses, _test_poses
      # create new position data
      new_pos = copy.deepcopy(UARM_TRAIN_POSITION_SAMPLE)
      new_pos['time'] = round(time.time() - _start_time, 3)
      new_pos['position'] = coord.copy()
      # add it to the history
      _recorded_poses.append(new_pos)
      # add it to the list of previous position, within our timeout range
      _test_poses.append(new_pos)
      while new_pos['time'] - _test_poses[0]['time'] > still_seconds:
        _test_poses = _test_poses[1:]

    def _is_moving():
      # wait until the timeout period has passed
      if time.time() - _start_time < still_seconds:
        return True
      # get the total distance moved, across all test positions
      # these are the positions with our timeout
      total_dist_moved = 0
      for i in range(1, len(_test_poses)):
        total_dist_moved += get_distance(
          _test_poses[i]['position'], _test_poses[i - 1]['position'])
      if total_dist_moved > still_distance:
        return True
      else:
        return False

    if method is None:
      method = lambda robot, poses, moving: moving

    # make sure the motors are turned off
    robot.disable_all_motors()
    _start_time = round(time.time(), 3)
    while method(robot, copy.deepcopy(_recorded_poses), _is_moving()):
      robot.update_position()
      if check and not robot.can_move_to(**robot.position):
        logger.info(
          'uArm not able to move to position: {0}'.format(robot.position))
        break
      else:
        _add_position(robot.position)
    _end_time = round(time.time(), 3)

    # save list of positions to disk
    save_data = copy.deepcopy(UARM_TRAIN_SAVED_DATA)
    save_data['samples'] = _recorded_poses
    save_data['hardware_settings'] = robot.hardware_settings
    save_data['time']['start'] = _start_time
    save_data['time']['end'] = _end_time
    save_data['time']['duration'] = round(_end_time - _start_time, 3)
    self._data[name] = save_data
    self._save_data()
    self.process(name)
    return self


  def process(self, name, filter=False, max_angle=None):

    def _create_rich_data(samples):
      # add 'duration', 'distance', 'speed', 'start', and 'end' properties
      rich_samples = []
      prev = samples[0]
      for d in samples:
        dist = round(get_distance(d['position'], prev['position']), 3)
        if dist != 0:
          d['start'] = prev['position']
          d['end'] = d['position']
          d['duration'] = round(d['time'] - prev['time'], 3)
          d['distance'] = dist
          d['speed'] = round(d['distance'] / d['duration'], 3)
          rich_samples.append(d)
          prev = d
      # remove unneeded raw properties, after we've used them for calculating
      for i in range(len(rich_samples)):
        del rich_samples[i]['position']
        del rich_samples[i]['time']
      return rich_samples


    if name not in self._data:
      raise ValueError('Not a recording: {0}'.format(name))

    raw_data = self._data[name]

    # filter out samples, using angle and distance
    filtered_data = copy.deepcopy(raw_data)
    if filter:
      filtered_data['samples'] = filter_absolute_data(
        filtered_data['samples'], max_angle)

    # add 'duration', 'distance', 'speed', 'start', and 'end' properties
    rich_data = copy.deepcopy(filtered_data)
    rich_data['samples'] = _create_rich_data(rich_data['samples'])

    # print('Raw Length: {0}, Filtered Length: {1}, Rich Length: {2}'.format(
    #   len(raw_data['samples']),
    #   len(filtered_data['samples']) if filter else None,
    #   len(rich_data['samples'])
    # ))

    self._processed_data[name] = rich_data
    return self

  def playback(self, robot, name, relative=False, speed=None, check=False):
    if name not in self._processed_data:
      raise ValueError('Recording not found: {0}'.format(name))
    data = copy.deepcopy(self._processed_data[name])
    samples = data['samples']
    if not len(samples):
      return self
    if relative:
      # get the relative offset from the robot's current position
      abs_start = robot.position
      pos_offset = {
        ax: abs_start[ax] - samples[0]['start'][ax]
        for ax in 'xyz'
      }
      # add that offset to all start and end samples positions
      for i in range(len(samples)):
        for pos in ['start', 'end']:
          samples[i][pos] = {
            ax: samples[i][pos][ax] + pos_offset[ax]
            for ax in 'xyz'
          }
    robot.push_settings()
    robot.move_to(**samples[0]['start'], check=check)
    if speed is not None:
      robot.speed(speed)
    for s in samples:
      if speed is None:
        robot.speed(s['speed'])
      robot.move_to(**s['end'], check=check)
      # TODO: include sleeps to make sure time is correct
    robot.pop_settings()
    return self


if __name__ == '__main__':
  from uarm import uarm_scan_and_connect

  # setup logging
  test_logger = logging.getLogger('uarm.swiftapi.record')
  test_logger.setLevel(logging.INFO)
  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)
  formatter = logging.Formatter('%(asctime)s - %(message)s')
  ch.setFormatter(formatter)
  test_logger.addHandler(ch)

  dir_path = os.path.dirname(os.path.realpath(__file__))
  file_path = os.path.join(dir_path, 'temp.json')
  if os.path.isfile(file_path):
    os.remove(file_path)

  robot = uarm_scan_and_connect()
  recorder = Recorder(file_path)

  print('Record with default motion detection. Waiting for touch...')
  robot.wait_for_touch()
  recorder.record(robot, 'test1')

  def _get_input(poses, pos, moving):
    res = input('ENTER=record, X+ENTER=stop: ')
    if len(res) == 0:
      return True
    elif 'x' in res.lower():
      return False
    else:
      return _get_input(poses, pos, moving)

  print('Recording with keyboard input...')
  recorder.record(robot, 'test2', method=_get_input)

  for name in ['test1', 'test2']:
    robot.home()
    print('{0}: Unfiltered Coordinates'.format(name))
    recorder.process(name, filter=False)
    recorder.playback(robot, name)
    robot.home()
    print('{0}: Filtered Coordinates'.format(name))
    recorder.process(name, filter=True)
    recorder.playback(robot, name)

  robot.sleep()
  os.remove(file_path)
