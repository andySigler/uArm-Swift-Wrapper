import argparse
import os

from uarm import uarm_scan_and_connect
from uarm.wrapper.swift_api_wrapper import UARM_DEFAULT_SPEED


def _record_with_keyboard(bot, recording):
    res = input('ENTER to record position, X+ENTER to stop recording: ')
    if len(res) == 0:
        return True   # return True will record the current position
    elif 'x' == res.lower():
        return False  # return False will end the recording
    else:
        return _record_with_keyboard(bot, recording)


parser = argparse.ArgumentParser()
parser.add_argument('--name', type=str)
parser.add_argument('--dir', type=str, default=None)
parser.add_argument('--mode', type=str, default='')
parser.add_argument('--auto', action='store_true')
parser.add_argument('--keys', action='store_true', default=True)
args = parser.parse_args()

if not args.name:
    raise ValueError('Name of recording must be passed with --name')
if not args.auto and not args.keys:
    raise ValueError('Recording must use either --auto or --keys')
if args.auto:
    args.keys = False

method = None
if args.keys:
    method = _record_with_keyboard

robot = uarm_scan_and_connect(settings_dir=args.dir)
print('About to record \"{0}\" to -> {1}'.format(
    args.name, robot.settings_directory))
if args.mode:
    robot.tool_mode(args.mode)
if args.auto:
    print('Waiting for user to move uArm...')
    robot.wait_for_touch()
robot.record(args.name, overwrite=True, method=method)
print('Recorded \"{0}\" to -> {1}'.format(
    args.name, robot.settings_directory))
res = input("Playback the recording? (default=no): ")
if res.lower()[0] == 'y':
    speed = None
    if args.keys:
        speed = UARM_DEFAULT_SPEED
    res = input("Filter the playback? (default=no): ")
    if res.lower()[0] == 'y':
        robot.process_recording(args.name, filter=True)
    robot.playback(args.name, speed=speed)
