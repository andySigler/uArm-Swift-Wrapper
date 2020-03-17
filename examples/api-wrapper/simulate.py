from uarm import uarm_create


# create an instance of `SwiftAPIWrapper`, but with no serial port connection
robot = uarm_create(simulate=True)
if robot.is_simulating():
    print('uArm is simulating')

# all commands can be ran on this "simulating" instance
# and it will pretend it is an actual uArm
# all commands will run immedately
robot.home()

robot.speed(100)
robot.acceleration(2)

robot.move_to(x=150, y=0, z=50)
for i in range(10):
    robot.move_relative(x=50, y=50, z=50)
    # position will continue to update while simulating
    print(robot.position)
    robot.move_relative(x=-50, y=-50, z=-50)
    # position will continue to update while simulating
    print(robot.position)
