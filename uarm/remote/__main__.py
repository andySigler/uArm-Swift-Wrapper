import argparse
import logging

from uarm.wrapper.swift_api_wrapper import uarm_create
from .uarm_osc_server import uarm_osc_server
from .uarm_osc_server import SWIFT_API_WRAPPER_OSC_DEFAULT_IP
from .uarm_osc_server import SWIFT_API_WRAPPER_OSC_DEFAULT_PORT_SERVER


def run_testing_client(ip, port):

  def _test_client_loop():
    import random
    import time
    from pythonosc import udp_client
    client = udp_client.SimpleUDPClient(ip, port)
    while True:
        r_pos = [random.randint(0, 100) for _ in 'xyz']
        client.send_message("/move_to", [port] + r_pos) # move command
        time.sleep(1)
        client.send_message("/position", [port])        # get coord
        time.sleep(1)
        client.send_message("/port", [port])            # get string
        time.sleep(1)
        client.send_message("/speed", [port])           # causes error
        time.sleep(1)
        client.send_message("/speed", [])               # causes error
        time.sleep(1)

  import threading
  client_thread = threading.Thread(target=_test_client_loop)
  client_thread.start()


parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str,
                    default=SWIFT_API_WRAPPER_OSC_DEFAULT_IP)
parser.add_argument('--port', type=int,
                    default=SWIFT_API_WRAPPER_OSC_DEFAULT_PORT_SERVER)
parser.add_argument('--test', action='store_true')
args = parser.parse_args()


# run a simple testing client, for development
if args.test:
  run_testing_client(args.ip, args.port)

# setup logging
osc_logger = logging.getLogger('uarm.swiftapi.wrapper.osc')
osc_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
ch.setFormatter(formatter)
osc_logger.addHandler(ch)

# create robot instance and run the OSC server
robot = uarm_create(simulate=True)
robot_server = uarm_osc_server(robot, ip=args.ip, port=args.port)
robot_server.serve_forever() # block forever
