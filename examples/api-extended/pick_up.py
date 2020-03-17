from uarm import uarm_scan_and_connect


robot = uarm_scan_and_connect()

# reset the uarm, and move it to it's centered position
robot.home()

# by default, the uArm is in "general" mode, which lets you use the air-pump
robot.mode('general') # this already default, so no need to run this
robot.move_to(x=150, z=10)
robot.wait_for_arrival()
robot.pump(True)

robot.move_relative(z=100)
robot.wait_for_arrival()
robot.pump(False)

# pump has a switch in the nozzle, to detect if it presses down on something
robot.move_to(x=150, z=10)
robot.wait_for_arrival()
if robot.is_pressing():
    print('Robot is pressing down on something')
else:
    print('Robot is NOT pressing down on something')
robot.move_relative(z=100)
robot.wait_for_arrival()

# if you instead want to use the gripper, change the mode to "pen_gripper"
robot.mode('pen_gripper')
robot.move_to(x=150, z=10)
robot.wait_for_arrival()
robot.grip(True)

robot.move_relative(z=100)
robot.wait_for_arrival()
robot.grip(False)
