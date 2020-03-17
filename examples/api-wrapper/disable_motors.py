import time

from uarm import uarm_scan_and_connect


robot = uarm_scan_and_connect()

# reset the uarm, and move it to it's centered position
robot.home()

# motors can be turned off on the uArm
# this allows it to not overheat, and to also be moved around by a person
# WARNING: if the motors are disabled while the arm is extend, the arm will
#          immediately drop down and potentially damage something
robot.disable_all_motors()
time.sleep(3)
robot.enable_all_motors()

# you can disable just the base (the base motor gets the hottest over time)
# this keeps the arm's elbow and wrist locked in position, but the base
# can be rotated freely by hand
robot.disable_base()
time.sleep(3)
robot.enable_all_motors()

# after disabling the base or all motors, a move command will automatically
# re-enable the motors
robot.disable_all_motors()
time.sleep(3)
robot.move_to(x=150, y=20, z=60)

# a common desire is to `home()` the robot, putting it in a safe position,
# and then disabling all the motors, so the arm doesn't fall
# This can be accomplished with the `sleep()` command
robot.sleep()
