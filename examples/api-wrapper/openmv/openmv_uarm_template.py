import json
import sensor


def uarm_setup(grayscale=False):
    sensor.reset()
    sensor.set_pixformat(sensor.GRAYSCALE if grayscale else sensor.RGB565)
    # image resolution affects the calibration data
    sensor.set_framesize(sensor.QVGA)
    # both rotate & mirror the image, so it's coordinates match the uArm's
    sensor.set_hmirror(True)
    # chop off the extra black spaces after rotation
    sensor.set_windowing((
        int((sensor.width() - sensor.height()) / 2), 0,
        sensor.height(), sensor.height()))
    # any other sensor configurations
    #      go here...
    # finally, skip some frames after configuring
    sensor.skip_frames()

def uarm_snapshot():
    img = sensor.snapshot()
    img.lens_corr(1.8)                  # flatten the image
    img.rotation_corr(z_rotation=90)    # rotate on read
    return img

def uarm_offset_in_image(img, x, y):
    return {
        'x': x - (img.width() / 2),
        'y': y - (img.height() / 2)
    }


uarm_setup()
while True:
    img = uarm_snapshot()
    blob_pos = uarm_offset_in_image(img, x=10, y=20)
    print(json.dumps(blob_pos))
