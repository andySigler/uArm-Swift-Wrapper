import time
from uarm import uarm_scan_and_connect


robot = uarm_scan_and_connect()

# reset the uarm, and move it to it's centered position
robot.home()

# the robot keeps track of it's position at all times
print(robot.position)
robot.move_to(x=150, y=0, z=50)
print(robot.position)
robot.move_relative(x=50, y=50, z=50)
print(robot.position)

# to explicitely ask the uArm hardware what it's position is,
# you can run `update_position()`
robot.update_position()
print(robot.position)

# each motor on the uArm has an encoder, so it can sense it's position
# even when all the motors are disabled
robot.sleep()
start_time = time.time()
# sleep for 5 seconds
# and use your hand to move the robot around and see the new positions printed
print('Disabled all motors for 5 seconds')
while time.time() - start_time < 5:
    robot.update_position()
    print(robot.position)

robot.home()

# using the encoders, the uArm can detect when a user touches the robot
# use the `wait_for_touch()` method to detect when a human touches the uArm
robot.move_to(x=150, y=0, z=120)
print('Waiting for touch...', end='')
robot.wait_for_touch()
print('touched!')

robot.sleep()
