from uarm import uarm_scan_and_connect

robot = uarm_scan_and_connect()

robot.home()

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

robot.sleep()
