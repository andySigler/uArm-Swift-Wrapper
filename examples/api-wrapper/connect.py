from uarm import uarm_scan, uarm_scan_and_connect


# automatically detect and connect to a uArm connected over USB
robot = uarm_scan_and_connect()

# disconnect and connect to the serial port at any point
robot.disconnect()
robot.connect()
print('Connected to:', robot.port)
robot.disconnect()

# scan for all connected uArm's
uarm_list = uarm_scan()

# the list of `SwiftAPIWrapper` intances are not connected yet
for r in uarm_list:
    r.connect()
    print('Connected to:', r.port)

for r in uarm_list:
    r.disconnect()
