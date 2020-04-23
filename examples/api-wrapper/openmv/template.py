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


uarm_setup(grayscale=False, resolution=3)
while True:
    img = uarm_snapshot(binary=False)
    blob_pos = uarm_offset_in_image(img, x=10, y=20)
    print(json.dumps(blob_pos))
