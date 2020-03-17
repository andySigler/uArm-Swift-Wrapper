from uarm import uarm_scan_and_connect


robot = uarm_scan_and_connect()

# reset the uarm, and move it to it's centered position
robot.home()

# rotate the wrist's servo motor the center position
robot.rotate_to(90)

# rotate it to one side, and then the other
robot.rotate_to(150)
robot.rotate_to(30)

# rotate a relative number of degrees
robot.rotate_relative(60)

# optionally set how many seconds to pause after rotating the wrist
robot.rotate_to(150, sleep=1)
robot.rotate_to(30, sleep=0)
