import copy

from pythonosc import dispatcher, osc_server, udp_client

from uarm import SwiftAPIWrapper


SWIFT_API_WRAPPER_OSC_DEFAULT_IP = '127.0.0.1'
SWIFT_API_WRAPPER_OSC_DEFAULT_PORT = 5005


def _call_object_method(obj_instance, attr_str, *args, **kwargs):
  if not hasattr(obj_instance, attr_str):
    raise RuntimeError(
      '{0} does not have method: {1}'.format(
        obj_instance.__class__.__name__, attr_str))
  try:
    attr = getattr(obj_instance, attr_str)
    if callable(attr):
      return attr(*args, **kwargs)
    else:
      return attr
  except Exception as e:
    return e


def _register_osc_handler(disp, obj, method, *args, **kwargs):
  disp.map(
    '/' + method,               # OSC filter
    _osc_server_handler,        # callback
    obj,                        # instance of API object
    method,                     # API method to be called
    args,                       # as list
    kwargs,                     # as dict
    needs_reply_address=True)   # include client's IP in callback


def _osc_send_reply(ip, port, method_str, data):

  # ensure data is a list
  if data is None:
    data = []
  elif isinstance(data, tuple):
    data = list(data)
  elif not isinstance(data, list):
    data = [data]

  # create flattened list
  trailing_uri = 'reply'
  reply_data = []
  for d in data:
    if isinstance(d, bool):
      reply_data.append(int(d))
    elif isinstance(d, dict):
      # TODO: so far, only XYZ coordinates need to be parsed from dicts
      reply_data += [d[ax] for ax in 'xyz']
    elif isinstance(d, Exception):
      reply_data.append(str(d))
      trailing_uri = 'error'
    elif isinstance(d, (str, int, float)):
      reply_data.append(d)

  # send the reply
  osc_uri = '/{0}/{1}'.format(method_str, trailing_uri)
  print('Reply - {0}:{1}{2} = {3}'.format(ip, port, osc_uri, reply_data))
  client = udp_client.SimpleUDPClient(ip, port)
  client.send_message(osc_uri, reply_data)


def _osc_server_handler(osc_ip, osc_uri, obj_args, *osc_args):
  if len(obj_args) < 4:
    raise RuntimeError(
      '_osc_server_handler() expected at least 4 args, got {1}'.format(len(obj_args)))
  if len(osc_args) == 0:
    raise RuntimeError(
      '_osc_server_handler() requires OSC value to include client port')

  # parse args
  osc_ip = osc_ip[0]
  obj_instance = obj_args[0]
  method_str = copy.deepcopy(obj_args[1])
  method_args = copy.deepcopy(obj_args[2])
  method_kwargs = copy.deepcopy(obj_args[3])
  osc_port = copy.deepcopy(osc_args[0])

  # include the received OSC value when calling the method
  osc_args = osc_args[1:] # remove the client IP address
  method_args = list(method_args)
  if osc_args:
    if isinstance(osc_args, (list, tuple)):
      method_args += list(osc_args)
    elif isinstance(osc_args, (str, float, int)):
      method_args.append(osc_args)

  # call the method
  print('Received - {0}{1} = {2}'.format(osc_ip, osc_uri, method_args))
  ret = _call_object_method(
    obj_instance, method_str, *method_args, **method_kwargs);

  # reply to the client with data
  _osc_send_reply(osc_ip, osc_port, method_str, ret)


def uarm_serve_osc(robot, ip=None, port=None):
  if ip is None:
    ip = SWIFT_API_WRAPPER_OSC_DEFAULT_IP
  if port is None:
    port = SWIFT_API_WRAPPER_OSC_DEFAULT_PORT
  disp = dispatcher.Dispatcher()
  for attr in dir(robot.__class__):
    for parent in robot.__class__.__bases__:
      if attr not in dir(parent) and not attr.startswith('_'):
        _register_osc_handler(disp, robot, attr)
  server = osc_server.ThreadingOSCUDPServer((ip, port), disp)
  server.serve_forever()


if __name__ == "__main__":
  robot = SwiftAPIWrapper(simulate=True)
  uarm_serve_osc(robot)
