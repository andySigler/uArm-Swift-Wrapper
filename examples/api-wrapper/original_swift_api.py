from uarm import uarm_scan_and_connect


robot = uarm_scan_and_connect()

# reset the uarm, and move it to it's centered position
robot.home()

# the `SwiftAPIWrapper` inherits all methods from the original `SwiftAPI`
# therefore, all methods and attributes from `SwiftAPI` can be used
print(robot.get_device_info())
swift.set_polar(stretch=200)
swift.set_polar(rotation=90)
swift.set_polar(height=150)

