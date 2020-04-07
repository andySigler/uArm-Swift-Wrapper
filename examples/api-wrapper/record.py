from uarm import uarm_scan_and_connect

robot = uarm_scan_and_connect()

robot.home()

robot.erase('my-recording')
robot.erase('my-recording-2')

print('Ready to record, start moving the robot by hand...')
robot.wait_for_touch()
robot.record('my-recording')

print('Done recording, playing it back')
robot.playback('my-recording')

print('Playback at a constant speed')
robot.playback('my-recording', speed=300)

print('Filter out unnecessary, intermediate motion (still buggy...)')
robot.process_recording('my-recording', filter=True)
robot.playback('my-recording')


def _record_with_keyboard(bot, recording):
    res = input('ENTER to record position, X+ENTER to stop recording')
    if len(res) == 0:
        return True   # return True will record the current position
    elif 'x' == res.lower():
        return False  # return False will end the recording
    else:
        return _record_on_input(bot, recording)


print('Create a recording using keyboard input')
robot.sleep()
robot.record('my-recording-2', method=_record_with_keyboard)
robot.playback('my-recording-2', speed=300)

robot.sleep()
