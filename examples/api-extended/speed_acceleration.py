from uarm import uarm_scan_and_connect


robot = uarm_scan_and_connect()

# speed is (almost) in mm/sec
# however, the actual speed of the uArm depends on which axes are moving
# the maximum speed is 600mm/sec
# the faster the speed, the more likely that an axis will "skip"

# reset the uarm, and move it to it's centered position
robot.home()
robot.move_to(x=150, y=0, z=40)

robot.speed(50)
robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)

robot.speed(100)
robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)

robot.speed(200)
robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)

robot.speed(400)
robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)

# accleration is (almost) in mm/sec/sec
# the maximum acceleration is 50mm/sec/sec
# the faster the acceleration, the more likely that an axis will "skip"

# reset the uarm, and move it to it's centered position
robot.home()
robot.speed(100)
robot.move_to(x=150, y=0, z=40)

robot.acceleration(0.5)
robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)

robot.acceleration(1)
robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)

robot.acceleration(3)
robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)

robot.acceleration(10)
robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)

robot.acceleration(30)
robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)
