import copy

from pythonosc import dispatcher, osc_server, udp_client

from uarm import SwiftAPIWrapper


SWIFT_API_WRAPPER_OSC_DEFAULT_IP = '127.0.0.1'
SWIFT_API_WRAPPER_OSC_DEFAULT_PORT = 5005


def call_object_method(obj_instance, method_str, *args, **kwargs):
  if not hasattr(obj_instance, method_str):
    raise RuntimeError(
      '{0} does not have method: {1}'.format(
        obj_instance.__class__.__name__, method_str))
  func = getattr(obj_instance, method_str)
  if callable(func):
    return func(*args, **kwargs)
  else:
    return func


def parse_osc_value_to_args(osc_args, args_list, kwargs_dict):
  args_list = list(args_list)
  if osc_args:
    if isinstance(osc_args, (list, tuple)):
      args_list += list(osc_args)
    elif isinstance(osc_args, (str, float, int)):
      args_list.append(osc_args)
  return (args_list, kwargs_dict)


def create_dispatch_args(obj, method, *args, **kwargs):
  dispatch_args = [
    '/' + method, osc_server_handler,
    obj, method, args, kwargs
  ]
  return dispatch_args


def register_method_as_osc_handler(disp, obj, method, *args, **kwargs):
  disp.map(*create_dispatch_args(
    obj, method, *args, **kwargs), needs_reply_address=True)


def osc_send_reply(ip, port, method_str, data):

  # ensure data is a list
  if data is None:
    data = []
  elif isinstance(data, tuple):
    data = list(data)
  elif not isinstance(data, list):
    data = [data]

  # create flattened list
  reply_data = []
  for d in data:
    if isinstance(d, bool):
      reply_data.append(int(d))
    elif isinstance(d, dict):
      # TODO: so far, only XYZ coordinates need to be parsed from dicts
      reply_data += [d[ax] for ax in 'xyz']
    elif isinstance(d, (str, int, float)):
      reply_data.append(d)

  # send the reply
  osc_uri = '/{0}/reply'.format(method_str)
  print('Reply - {0}:{1}{2} = {3}'.format(ip, port, osc_uri, reply_data))
  client = udp_client.SimpleUDPClient(ip, port)
  client.send_message(osc_uri, reply_data)


def osc_server_handler(osc_ip, osc_uri, obj_args, *osc_args):
  if len(obj_args) < 4:
    raise RuntimeError(
      'osc_server_handler() expected at least 4 args, got {1}'.format(len(obj_args)))
  if len(osc_args) == 0:
    raise RuntimeError(
      'osc_server_handler() requires OSC value to include client port')

  # parse args
  osc_ip = osc_ip[0]
  obj_instance = obj_args[0]
  method_str = copy.deepcopy(obj_args[1])
  method_args = copy.deepcopy(obj_args[2])
  method_kwargs = copy.deepcopy(obj_args[3])
  osc_port = copy.deepcopy(osc_args[0])

  # include the received OSC value when calling the method
  osc_args = osc_args[1:]
  method_args, method_kwargs = parse_osc_value_to_args(
    osc_args, method_args, method_kwargs)

  # call the method
  print('Received - {0}{1} = {2}'.format(osc_ip, osc_uri, method_args))
  ret = call_object_method(
    obj_instance, method_str, *method_args, **method_kwargs);

  # reply to the client with data
  osc_send_reply(osc_ip, osc_port, method_str, ret)


def robot_osc_run(robot, ip=None, port=None):
  if ip is None:
    ip = SWIFT_API_WRAPPER_OSC_DEFAULT_IP
  if port is None:
    port = SWIFT_API_WRAPPER_OSC_DEFAULT_PORT
  disp = dispatcher.Dispatcher()
  register_method_as_osc_handler(disp, robot, 'port', reply=True)
  register_method_as_osc_handler(disp, robot, 'push_settings')
  register_method_as_osc_handler(disp, robot, 'pop_settings')
  register_method_as_osc_handler(disp, robot, 'wait_for_arrival')
  register_method_as_osc_handler(disp, robot, 'mode')
  register_method_as_osc_handler(disp, robot, 'speed')
  register_method_as_osc_handler(disp, robot, 'acceleration')
  register_method_as_osc_handler(disp, robot, 'update_position')
  register_method_as_osc_handler(disp, robot, 'get_base_angle', reply=True)
  register_method_as_osc_handler(disp, robot, 'position', reply=True)
  register_method_as_osc_handler(disp, robot, 'wrist_angle', reply=True)
  register_method_as_osc_handler(disp, robot, 'can_move_to', reply=True)
  register_method_as_osc_handler(disp, robot, 'can_move_relative', reply=True)
  register_method_as_osc_handler(disp, robot, 'move_to')
  register_method_as_osc_handler(disp, robot, 'move_relative')
  register_method_as_osc_handler(disp, robot, 'rotate_to')
  register_method_as_osc_handler(disp, robot, 'rotate_relative')
  register_method_as_osc_handler(disp, robot, 'disable_base')
  register_method_as_osc_handler(disp, robot, 'disable_all_motors')
  register_method_as_osc_handler(disp, robot, 'enable_all_motors')
  register_method_as_osc_handler(disp, robot, 'pump')
  register_method_as_osc_handler(disp, robot, 'grip')
  register_method_as_osc_handler(disp, robot, 'is_pressing', reply=True)
  register_method_as_osc_handler(disp, robot, 'home')
  register_method_as_osc_handler(disp, robot, 'probe')
  register_method_as_osc_handler(disp, robot, 'sleep')
  register_method_as_osc_handler(disp, robot, 'wait_for_touch')
  server = osc_server.ThreadingOSCUDPServer((ip, port), disp)
  server.serve_forever()


if __name__ == "__main__":
  robot = SwiftAPIWrapper(simulate=True)
  robot_osc_run(robot)
