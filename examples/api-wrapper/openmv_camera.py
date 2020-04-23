'''

The Python wrapper's method for tracking positions seen with the OpenMV
require that the OpenMV is running a script based on the template:

  -> https://github.com/andysigler/uArm-Python-Wrapper/blob/master/examples/openmv/template.py


To make the OpenMV camera more accurate, it is recommended to run the
calibration process. Read more here:

  -> https://github.com/andysigler/uArm-Python-Wrapper/blob/master/CALIBRATION.md#openmv-camera

'''

from uarm import uarm_scan_and_connect
from uarm import offset
from uarm import openmv


robot = uarm_scan_and_connect()
robot.tool_mode('general').home()

camera = openmv.OpenMV(robot)

blob_height = 15

# move the camera up high
camera.move_to(x=150, y=0, z=120)
robot.wait_for_arrival()

# get the position of the object (assume OpenMV uses blob detection)
# NOTE: OpenMV needs to be programmed separately
blob_pos_in_image = camera.read_json()
blob_pos = camera.position_from_image(
    object_height=blob_height, **blob_pos_in_image)

# move to the object's location and pick it up
robot.move_to(**blob_pos).pump(True)
robot.move_relative(z=20)
robot.pump(False) # drop it

robot.sleep()
