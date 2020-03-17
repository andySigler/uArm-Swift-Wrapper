from uarm import uarm_scan_and_connect


robot = uarm_scan_and_connect()

robot.home().speed(100).acceleration(5)
robot.move_to(x=150).move_to(y=100, z=120).move_to(y=-100, z=50)
robot.move_relative(x=20).move_relative(y=100).move_relative(z=20)
