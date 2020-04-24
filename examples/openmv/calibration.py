'''

This script is for the OpenMV, to be ran during calibration.

Flash this script to an OpenMV attached to the uArm, and running the
calibration script with the following command:

  python -m uarm.openmv.calibrate

Read the following for more details:

  https://github.com/andysigler/uArm-Python-Wrapper/blob/master/CALIBRATION.md

'''

import json
import sensor


def uarm_setup(grayscale=False, resolution=2):
    sensor.reset()
    sensor.set_pixformat(sensor.GRAYSCALE if grayscale else sensor.RGB565)
    # image resolution affects the calibration data
    size_lookup = [
        sensor.QQQQVGA, sensor.QQQVGA, sensor.QQVGA, sensor.QVGA, sensor.VGA]
    sensor.set_framesize(size_lookup[resolution])
    # both rotate & mirror the image, so it's coordinates match the uArm's
    sensor.set_hmirror(True)
    # chop off the extra black spaces after rotation
    sensor.set_windowing((
        int((sensor.width() - sensor.height()) / 2), 0,
        sensor.height(), sensor.height()))
    # any other sensor configurations go here...
    # finally, skip some frames after configuring
    sensor.skip_frames()


def uarm_snapshot(binary=False):
    img = sensor.snapshot()
    img.lens_corr(1.8)                  # flatten the image
    img.rotation_corr(z_rotation=90)    # rotate on read
    if binary:
        value = img.get_histogram().get_threshold().value()
        img.binary([(0, value)], invert=True)
    return img


def uarm_offset_in_image(img, x, y):
    # convert image location to offset from center, in percentage of screen size
    # therefore the image's resolution can change without affecting calibration
    size = max(img.width(), img.height())
    ox = x - (img.width() / 2) # pixels away from center
    oy = y - (img.height() / 2)
    rx = ox / (size / 2) # percentage of screen-size away from center
    ry = oy / (size / 2)
    return {
        'x': rx,
        'y': ry
    }


uarm_setup(grayscale=True, resolution=3)
while True:
    img = uarm_snapshot(binary=True)
    # get the black blobs from the image
    blobs = img.find_blobs(
        [(127, 0)], pixels_threshold=10, area_threshold=10, merge=True)
    # ignore large or non-circular blobs
    size = max(img.width(), img.height())
    max_size = size * 0.5
    small_blobs = [
        b
        for b in blobs
        if max(b.w(), b.h()) < max_size and abs(b.w() - b.h()) < (size * 0.05)
    ]
    # visualize filtered blobs
    for b in small_blobs:
        img.draw_rectangle(b.rect(), color=127)
    # get their offset positions
    calibration_points = [
        uarm_offset_in_image(img, x=b.cxf(), y=b.cyf())
        for b in small_blobs
    ]
    # print to serial port
    print(json.dumps(calibration_points))
