from uarm import uarm_scan_and_connect


robot = uarm_scan_and_connect()

# reset the uarm, and move it to it's centered position
robot.home()

# NOTE: learn more about the uArm's coordinate system in their manual
#       `uArm-Python-SDK -> doc -> manuals -> Quick Starter Guide`

# move to absolute coordinates
robot.move_to(x=150)
robot.move_to(y=100, z=120)
robot.move_to(y=-100, z=50)

# move to relative coordinates
robot.move_relative(x=20)
robot.move_relative(y=100)
robot.move_relative(z=20)

# Telling the robot to move will send a command over the USB serial port
# however, it might still be moving when the Python command returns.
# If you need to know when it is finished moving, using `wait_for_arrival()`

# A minor issue with this is that movement will be slightly less smooth,
# because you are waiting for the device to stop while sending it more data

robot.move_to(x=150, y=100)
robot.wait_for_arrival() # returns when the robot has stopped moving
