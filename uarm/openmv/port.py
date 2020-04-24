import json
import logging
import time

import serial
from serial.tools.list_ports import comports


OPENMV_PORT_DEFAULT_BAUDRATE = 115200
OPENMV_PORT_DEFAULT_TIMEOUT_SEC = 2
OPENMV_PORT_DEFAULT_RETRIES = 3
OPENMV_PORT_DEFAULT_MIN_DATA_LENGTH = 10

logger = logging.getLogger('uarm.openmv.port')


def find_camera_port():
    # TODO: smart way to discover OpenMV serial ports
    return '/dev/tty.usbmodem0000000000111'


class OpenMVPort(serial.Serial):
    def __init__(self,
                 port=None,
                 baudrate=None,
                 timeout=None,
                 min_data_length=OPENMV_PORT_DEFAULT_MIN_DATA_LENGTH,
                 stay_open=False):
        self._stay_open = stay_open
        self._min_data_length = min_data_length if min_data_length else OPENMV_PORT_DEFAULT_MIN_DATA_LENGTHe
        # init PySerial before giving it port so it doesn't auto-open
        super().__init__()
        self.port = port if port else find_camera_port()
        self.baudrate = baudrate if baudrate else OPENMV_PORT_DEFAULT_BAUDRATE
        self.timeout = timeout if timeout else OPENMV_PORT_DEFAULT_TIMEOUT_SEC

    def read_line(self, retries=OPENMV_PORT_DEFAULT_RETRIES, parser=None):

        def attempt_retry(exception):
            if retries > 0:
                logger.info('OpenMV retrying read:', retries)
                return self.read_json(retries=retries - 1)
            else:
                raise exception

        # make sure the port is open
        if not self.is_open:
            self.open()
        # clear the input buffer of previously sent data
        while self.in_waiting > self._min_data_length:
            self.readline() # reset_input_buffer() doesn't always work...
        # read the next line
        data = self.readline()
        # retry if there's no data
        if not data:
            logger.info('Camera returned no data')
            return attempt_retry(RuntimeError('Camera returned no data'))
        logger.info(data)
        # parse the json
        if parser and callable(parser):
            try:
                data = parser(data)
            except Exception as e:
                logger.exception()
                return attempt_retry(e)
        # close the port if required
        if not self._stay_open:
            self.close()
        return data


    def read_json(self, retries=OPENMV_PORT_DEFAULT_RETRIES):
        return self.read_line(retries=retries, parser=json.loads)
