import logging

from .measurements import get_offset_in_mode
from .helpers import get_offset_position, get_position_for_offset_target_at


logger = logging.getLogger('uarm.offset.offset')


class Offset(object):

    def __init__(self, robot, general_offset):
        self._robot = robot
        self._general_offset = general_offset

    @property
    def offset(self):
        return get_offset_in_mode(
            self._robot.get_tool_mode(), self._general_offset)

    @property
    def position(self):
        return get_offset_position(self._robot.position, self.offset)

    def move_to(self, x=None, y=None, z=None, **kwargs):
        openmv_target = self.position
        if x is not None:
            openmv_target['x'] = x
        if y is not None:
            openmv_target['y'] = y
        if z is not None:
            openmv_target['z'] = z
        uarm_target = get_position_for_offset_target_at(
            openmv_target, self.offset)
        kwargs.update(uarm_target)
        self._robot.move_to(**kwargs)
        return self

    def move_relative(self, x=None, y=None, z=None, **kwargs):
        openmv_target = self.position
        if x is not None:
          openmv_target['x'] += x
        if y is not None:
          openmv_target['y'] += y
        if z is not None:
          openmv_target['z'] += z
        kwargs.update(openmv_target)
        self.move_to(**kwargs)
        return self
