import copy

from uarm.offset.helpers import cartesian_to_polar
from uarm.offset.helpers import subtract_positions, add_positions
from uarm.offset.measurements import get_openmv_offset
from uarm.openmv.openmv import UARM_OPENMV_DEFAULT_CALIBRATION
from uarm.openmv.openmv import UARM_OPENMV_CALIBRATION_FILE_NAME


UARM_OPENMV_CALIBRATION_POINTS_DISTANCE = 20
# TODO: line up with printed calibration image
UARM_OPENMV_CALIBRATION_HEIGHTS = [180, 60]


def organize_calibration_points(points_list):
    x_sorted = sorted(points_list, key=lambda p: p['x'])
    y_sorted = sorted(x_sorted[1:-1], key=lambda p: p['y'])
    return {
        'left': x_sorted[0],
        'bottom': y_sorted[0],
        'center': y_sorted[1],
        'top': y_sorted[2],
        'right': x_sorted[-1]
    }


def read_sorted_points(camera):
    points = camera.read_json()
    if len(points) != 5:
        ValueError(
            'Read wrong number of calibration points, got {0}'.format(
                len(points)))
    for i in range(len(points)):
        points[i]['z'] = 0 # add Z positions to all points
    return organize_calibration_points(points)


def read_average_sorted_points(camera, samples=5):
    points_samples = [
        read_sorted_points(camera)
        for i in range(samples)
    ]
    sum_points = {
        key: add_positions(*[p[key] for p in points_samples])
        for key in points_samples[0].keys()
    }
    return {
        key: {
            ax: sum_points[key][ax] / samples
            for ax in 'xyz'
        }
        for key in sum_points.keys()
    }


def calculate_image_to_mm(points):
    x_offset = subtract_positions(points['right'], points['left'])
    y_offset = subtract_positions(points['top'], points['bottom'])
    x_dist, _, _ = cartesian_to_polar(**x_offset)
    y_dist, _, _ = cartesian_to_polar(**y_offset)
    x_image_to_mm = UARM_OPENMV_CALIBRATION_POINTS_DISTANCE / x_dist
    y_image_to_mm = UARM_OPENMV_CALIBRATION_POINTS_DISTANCE / y_dist
    return {'x': x_image_to_mm, 'y': y_image_to_mm}


def calculate_image_offset_mm(points, image_to_mm):
    return {
        ax: points['center'][ax] * image_to_mm[ax]
        for ax in 'xy'
    }


def create_calibration_data(camera):
    sorted_points = read_average_sorted_points(camera)
    image_to_mm = calculate_image_to_mm(sorted_points)
    image_to_mm['z'] = camera.position['z']
    angled_offset_mm = calculate_image_offset_mm(sorted_points, image_to_mm)
    angled_offset_mm['z'] = camera.position['z']
    return {
        'position': camera.position,
        'image_to_mm': image_to_mm,
        'angled_offset_mm': angled_offset_mm
    }


def calculate_offset_function(data):

    def _get_slope_bias(top, bottom, calculate_bias=True):
        z_top = top['z']
        bias = {'x': 0, 'y': 0}
        if calculate_bias:
            travel_z = top['z'] - bottom['z']
            z_scaler = bottom['z'] / travel_z
            # find the bias at z=0
            diff = subtract_positions(top, bottom)
            bias = {ax: bottom[ax] - (diff[ax] * z_scaler) for ax in 'xy'}
        # find the amount it shifted from z=0 to z=z_top
        actual_diff = {ax: top[ax] - bias[ax] for ax in 'xy'}
        # find the slope for z=?
        slope = {ax: actual_diff[ax] / z_top for ax in 'xy'}
        return (slope, bias)


    # find XY offset at z=0
    top_offset_mm = data[0]['angled_offset_mm']
    bottom_offset_mm = data[1]['angled_offset_mm']
    top_img_to_mm = data[0]['image_to_mm']
    bottom_img_to_mm = data[1]['image_to_mm']

    slope_offset_mm, bias_offset_mm = _get_slope_bias(
        top_offset_mm, bottom_offset_mm, calculate_bias=False)
    slope_img_to_mm, bias_img_to_mm = _get_slope_bias(
        top_img_to_mm, bottom_img_to_mm)

    new_data = copy.deepcopy(UARM_OPENMV_DEFAULT_CALIBRATION)
    new_data['angled_offset_mm']['slope'] = slope_offset_mm
    new_data['angled_offset_mm']['bias'] = bias_offset_mm
    new_data['image_to_mm']['slope'] = slope_img_to_mm
    new_data['image_to_mm']['bias'] = bias_img_to_mm
    return new_data


if __name__ == '__main__':
    import atexit
    from pprint import pprint
    import time

    from uarm import uarm_scan_and_connect
    from uarm import openmv

    robot = uarm_scan_and_connect()
    atexit.register(robot.sleep)

    camera = openmv.OpenMV(robot)
    camera.calibration_default()
    camera._general_offset = get_openmv_offset('general') # default offset
    robot.hardware_settings_default().tool_mode('general').home()

    robot.disable_all_motors()
    input('place robot on center of calibration dots, and press ENTER')
    robot.enable_all_motors()
    robot.update_position()
    start_pos = robot.position

    # hover the camera over the starting point
    camera.move_relative(z=15)
    camera.move_to(x=start_pos['x'], y=start_pos['y'])

    robot.push_settings()
    robot.speed(50).acceleration(0.5)
    calibration_data = []
    for z in UARM_OPENMV_CALIBRATION_HEIGHTS:
        camera_pos = start_pos.copy()
        camera_pos['z'] = z
        camera.move_to(**camera_pos)
        robot.wait_for_arrival()
        time.sleep(2)
        data = create_calibration_data(camera)
        calibration_data.append(data)
    robot.pop_settings()

    print('Calibration Data:')
    pprint(calibration_data)

    camera_functions = calculate_offset_function(calibration_data)
    print('\nCalibration Functions:')
    pprint(camera_functions)

    camera._calibration = camera_functions
    camera.save_calibration()
