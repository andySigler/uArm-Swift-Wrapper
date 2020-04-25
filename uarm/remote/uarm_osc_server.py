import copy
import logging
import sys

from pythonosc import dispatcher, osc_server, udp_client

from uarm.wrapper.swift_api_wrapper import SwiftAPIWrapper


logger = logging.getLogger('uarm.swiftapi.wrapper.osc')


SWIFT_API_WRAPPER_OSC_DEFAULT_IP = '127.0.0.1'
SWIFT_API_WRAPPER_OSC_DEFAULT_PORT_SERVER = 5115

SWIFT_API_WRAPPER_COMMAND_URI = '/{method}'
SWIFT_API_WRAPPER_REPLY_URI = '/{method}/reply'
SWIFT_API_WRAPPER_ERROR_URI = '/{method}/error'

SWIFT_API_WRAPPER_OSC_ARGS_INDEX_PORT = 0
SWIFT_API_WRAPPER_OSC_ARGS_INDEX_ARGS = 1
SWIFT_API_WRAPPER_OSC_ARGS_MIN_LENGTH = 1

SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_ROBOT = 0
SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_METHOD = 1
SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_ARGS = 2
SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_KWARGS = 3
SWIFT_API_WRAPPER_INTERNAL_ARGS_LENGTH = 4


class SwiftAPIWrapperOSCException(Exception):
  pass


def _uarm_osc_server_call_method(robot, attr_str, *args, **kwargs):
  if not hasattr(robot, attr_str):
    raise SwiftAPIWrapperOSCException(
      '{0} does not have method: {1}'.format(SwiftAPIWrapper, attr_str))
  try:
    attr = getattr(robot, attr_str)
    if callable(attr):
      return attr(*args, **kwargs)
    else:
      return attr
  except Exception as e:
    return e


def _uarm_osc_server_format_internal_args(robot, method, args, kwargs):
  disp_map_args = [None] * SWIFT_API_WRAPPER_INTERNAL_ARGS_LENGTH
  disp_map_args[SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_ROBOT] = robot
  disp_map_args[SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_METHOD] = method
  disp_map_args[SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_ARGS] = args
  disp_map_args[SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_KWARGS] = kwargs
  return disp_map_args


def _uarm_osc_server_parse_osc_args(osc_ip, osc_uri, osc_args):
  if len(osc_args) < SWIFT_API_WRAPPER_OSC_ARGS_MIN_LENGTH:
    raise SwiftAPIWrapperOSCException('Not enough OSC arguments to parse')
  osc_ip = str(osc_ip[0])  # comes in as tuple
  osc_port = int(osc_args[SWIFT_API_WRAPPER_OSC_ARGS_INDEX_PORT])
  osc_args = list(osc_args[SWIFT_API_WRAPPER_OSC_ARGS_INDEX_ARGS:])
  return (osc_ip, osc_port, osc_args)


def _uarm_osc_server_parse_internal_args(internal_args):
  if len(internal_args) < SWIFT_API_WRAPPER_INTERNAL_ARGS_LENGTH:
    raise SwiftAPIWrapperOSCException(
      'Expected at least {0} args, got {1}'.format(
        SWIFT_API_WRAPPER_INTERNAL_ARGS_LENGTH, len(internal_args)))
  # parse args set as internal defaults
  robot = internal_args[SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_ROBOT]
  method_str = str(internal_args[SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_METHOD])
  default_args = list(
    internal_args[SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_ARGS])
  default_kwargs = internal_args[SWIFT_API_WRAPPER_INTERNAL_ARGS_INDEX_KWARGS]
  return (robot, method_str, default_args, default_kwargs)


def _uarm_osc_server_register(disp, robot, method, *args, **kwargs):
  disp_map_args = _uarm_osc_server_format_internal_args(
    robot, method, args, kwargs)
  disp.map(
    SWIFT_API_WRAPPER_COMMAND_URI.format(method=method),  # OSC filter
    _uarm_osc_server_handler,                              # callback
    *disp_map_args,
    needs_reply_address=True)             # add client IP to callback


def _uarm_osc_server_reply(ip, port, method_str, data):

  # ensure data is a list
  if data is None:
    data = []
  elif isinstance(data, tuple):
    data = list(data)
  elif not isinstance(data, list):
    data = [data]

  # create flattened list
  response_uri = copy.copy(SWIFT_API_WRAPPER_REPLY_URI)
  reply_data = []
  for d in data:
    if isinstance(d, bool):
      reply_data.append(int(d))
    elif isinstance(d, dict):
      # TODO: so far, only XYZ coordinates need to be parsed from dicts
      reply_data += [d[ax] for ax in 'xyz']
    elif isinstance(d, Exception):
      reply_data.append(str(d))
      response_uri = copy.copy(SWIFT_API_WRAPPER_ERROR_URI)
    elif isinstance(d, (str, int, float)):
      reply_data.append(d)

  # send the reply
  osc_uri = response_uri.format(method=method_str)
  logger.info(
    'Reply - {0}:{1}{2} = {3}'.format(ip, port, osc_uri, reply_data))
  client = udp_client.SimpleUDPClient(ip, port)
  client.send_message(osc_uri, reply_data)


def _uarm_osc_server_handler(osc_ip, osc_uri, default_args, *osc_args):
  logger.debug('Handler called: {uri}'.format(uri=osc_uri))
  try:
    # parse the recieved OSC args, and the default internal args
    parsed_osc_args = _uarm_osc_server_parse_osc_args(
      osc_ip, osc_uri, osc_args)
    (osc_ip, osc_port, osc_args) = parsed_osc_args
    parsed_default_args = _uarm_osc_server_parse_internal_args(default_args)
    (robot, method_str, default_args, default_kwargs) = parsed_default_args

    # swap in the received OSC arguments, to replace any defaults
    default_args = copy.deepcopy(default_args)
    default_args = osc_args + default_args[len(osc_args):]

    # call the method
    logger.info(
      'Received - {0}{1} = {2}'.format(osc_ip, osc_uri, default_args))
    ret = _uarm_osc_server_call_method(
      robot, method_str, *default_args, **default_kwargs);

    # reply to the client with data
    _uarm_osc_server_reply(osc_ip, osc_port, method_str, ret)
  except SwiftAPIWrapperOSCException:
    logger.exception('Error handling OSC filter: {0}'.format(osc_uri))


def uarm_osc_server_gen_manifest():
  manifest = {}
  for attr in dir(SwiftAPIWrapper):
    for parent in SwiftAPIWrapper.__bases__:
      if attr not in dir(parent) and not attr.startswith('_'):
        manifest[attr] = {'method': attr, 'arguments': []}
        func = getattr(SwiftAPIWrapper, attr)
        if callable(func):
          arg_count = func.__code__.co_argcount
          arg_names = func.__code__.co_varnames
          func_args = arg_names[1:arg_count]
          manifest[attr]['arguments'] = func_args
  return manifest


def uarm_osc_server(robot, ip=None, port=None):
  if not isinstance(robot, SwiftAPIWrapper):
    raise TypeError(
      'OSC Server requires SwiftAPIWrapper, not {0}'.format(
        robot.__class__.__name__))
  if ip is None:
    ip = SWIFT_API_WRAPPER_OSC_DEFAULT_IP
  if port is None:
    port = SWIFT_API_WRAPPER_OSC_DEFAULT_PORT_SERVER
  # auto-register all methods as OSC handlers
  disp = dispatcher.Dispatcher()
  for method in uarm_osc_server_gen_manifest().keys():
    _uarm_osc_server_register(disp, robot, method)
  logger.info('Serving at {ip}:{port}'.format(
    ip=ip, port=port))
  return osc_server.ThreadingOSCUDPServer((ip, port), disp)

