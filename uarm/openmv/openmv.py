from .port import OpenMVPort
from uarm.offset import Offset
from uarm.offset.measurements import get_openmv_offset
from uarm.offset.helpers import get_offset_position


class OpenMV(Offset):

    def __init__(self, robot, port=None, baudrate=None):
        self._port = OpenMVPort(port=port, baudrate=baudrate)
        super().__init__(robot, get_openmv_offset('general'))

    def read(self):
        return self._port.read_json()

    def get_position_from_image(self, image_offset):
        return get_offset_position(
            self._robot.position, [image_offset, self.offset])

