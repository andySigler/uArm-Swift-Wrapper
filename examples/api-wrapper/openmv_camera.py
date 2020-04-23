from uarm import uarm_scan_and_connect
from uarm import offset
from uarm import openmv


robot = uarm_scan_and_connect()
robot.tool_mode('general').home()

camera = openmv.OpenMV(robot)

# move the camera up high
camera.move_to(x=150, y=0, z=120)

# get the position of the object (assume OpenMV uses blob detection)
# NOTE: OpenMV needs to be programmed separately
blob_pos_in_image = camera.read_json()
blob_pos = camera.position_from_image(**blob_pos_in_image)
blob_pos['z'] = 15  # can't accurately get height from camera

# move to the object's location and pick it up
robot.move_to(**blob_pos).pump(True)
robot.move_relative(z=20)
robot.pump(False) # drop it

robot.sleep()
