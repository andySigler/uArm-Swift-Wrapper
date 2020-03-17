from uarm import uarm_scan_and_connect


robot = uarm_scan_and_connect()

# reset the uarm, and move it to it's centered position
robot.home()
robot.move_to(x=150, y=0, z=40)

# save the current speed/acclerations settings
robot.push_settings()

# change the speed/acceleration
robot.speed(200)
robot.acceleration(10)

robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)

# restore the original speed/acceleration settings
robot.pop_settings()


# you can use push/pop in a "nested" way

# save the current speed/acclerations settings
robot.push_settings()

# change the speed/acceleration, and move
robot.speed(200)
robot.acceleration(10)
robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)

# again, save the current speed/acclerations settings
robot.push_settings()

# slow the speed/acceleration, and move
robot.speed(100)
robot.acceleration(2)
robot.move_relative(x=50, y=50, z=50)
robot.move_relative(x=-50, y=-50, z=-50)

# restore to the first change in speed/acceleration
robot.pop_settings()

# restore to the original speed/acceleration
robot.pop_settings()
