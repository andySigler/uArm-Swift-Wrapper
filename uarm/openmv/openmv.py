import copy
import json
import logging
import os

from uarm.openmv.port import OpenMVPort
from uarm.offset import Offset
from uarm.offset.measurements import get_openmv_offset
from uarm.offset.helpers import get_offset_position
from uarm.offset.helpers import add_positions, subtract_positions


UARM_OPENMV_CALIBRATION_FILE_NAME = 'openmv_calibration.json'

UARM_OPENMV_DEFAULT_CALIBRATION = {
    'angled_offset_mm': {
        'bias': {'x': 0, 'y': 0},
        'slope': {'x': 0, 'y': 0}
    },
    'image_to_mm': {
        'bias': {'x': -0.075, 'y': -0.25},
        'slope': {'x': 0.42, 'y': 0.42}
    }
}


logger = logging.getLogger('uarm.openmv.openmv')


class OpenMV(Offset):

    def __init__(self, robot, port=None, baudrate=None):
        self._port = OpenMVPort(port=port, baudrate=baudrate)
        self._calibration = copy.deepcopy(UARM_OPENMV_DEFAULT_CALIBRATION)
        super().__init__(robot, get_openmv_offset('general'))
        self.load_calibration()

    @property
    def calibration_path(self):
        return os.path.join(
            self._robot.settings_directory, UARM_OPENMV_CALIBRATION_FILE_NAME)

    def calibration_default(self):
        self._calibration = copy.deepcopy(UARM_OPENMV_DEFAULT_CALIBRATION)
        return self

    def load_calibration(self):
        if not os.path.isfile(self.calibration_path):
            # just use the default
            return self
        read_data = {}
        with open(self.calibration_path, 'r') as f:
            read_data = f.read()
        try:
          read_data = json.loads(read_data)
        except:
          read_data = copy.deepcopy(UARM_OPENMV_DEFAULT_CALIBRATION)
        for key, item in UARM_OPENMV_DEFAULT_CALIBRATION.items():
          if key not in read_data:
            read_data[key] = copy.deepcopy(item)
        self._calibration = copy.deepcopy(read_data)
        return self

    def save_calibration(self):
        calibration_json = json.dumps(self._calibration, indent=4)
        with open(self.calibration_path, 'w') as f:
            f.write(calibration_json)
        return self

    def read_json(self):
        return self._port.read_json()

    def read_line(self):
        return self._port.read_line()

    def position_from_image(self, image_offset, object_height=0):
        height = self.position['z']
        image_to_mm = self._get_image_to_mm_at_height(height)
        angled_offset_mm = self._get_angled_offset_mm_at_height(height)
        image_offset_mm = {
            ax: (image_offset[ax] * image_to_mm[ax]) - angled_offset_mm[ax]
            for ax in 'xy'
        }
        image_offset_mm['z'] = 0
        img_pos = get_offset_position(
            self._robot.position, [image_offset_mm, self.offset])
        img_pos['z'] = object_height
        if object_height == 0 or height == 0:
            return img_pos
        # include the object's height
        height_scaler = (object_height / 2) / height
        real_img_offset = subtract_positions(img_pos, self.position)
        real_offset = {
            ax: real_img_offset[ax] - (real_img_offset[ax] * height_scaler)
            for ax in 'xy'
        }
        img_pos = add_positions(self.position, real_offset)
        img_pos['z'] = object_height
        return img_pos

    def _calculate_calibration(self, height, calibration_key):
        bias = self._calibration[calibration_key]['bias']
        slope = self._calibration[calibration_key]['slope']
        return {
            ax: (slope[ax] * height) + bias[ax]
            for ax in 'xy'
        }

    def _get_image_to_mm_at_height(self, height):
        return self._calculate_calibration(height, 'image_to_mm')

    def _get_angled_offset_mm_at_height(self, height):
        return self._calculate_calibration(height, 'angled_offset_mm')


if __name__ == '__main__':
    import time
    from uarm import uarm_scan_and_connect
    robot = uarm_scan_and_connect()
    robot.tool_mode('general').home()
    camera = OpenMV(robot)
    robot.acceleration(1)
    robot.move_to(x=150, y=0, z=100).wait_for_arrival()
    time.sleep(1)
    raw_poses = camera.read_json()
    blob_poses = [camera.position_from_image(d) for d in raw_poses]
    for blob_pos in blob_poses:
        hover_pos = blob_pos.copy()
        hover_pos['z'] += 5
        robot.move_to(**hover_pos).move_to(**blob_pos).move_to(**hover_pos)
    robot.sleep()
