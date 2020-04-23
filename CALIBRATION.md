# Calibration

Some uArm settings would be nice if they could be saved, so that when you restart those settings are still there. That's what calibrations are for.

Currently, there are three things that can be calibrated and saved for later:

1. [Z Offset](#z-offset)
2. [Wrist Offset](#wrist-offset)
3. [OpenMV Camera](#openmv-camera)

These settings are saved in a file on the machine running the script, and default to the location of the `uarm` installation, in a folder called `.hardware_settings`.

To save different calibrations for different projects/directories, you can set the folder where calibrations are stored during initialization of the robot:

```python
robot = uarm_scan_and_connect(settings_dir='path/to/settings/directory')
```

## Z Offset

Sometimes the Z position does not line up with what you have put on the end of the uArm. Like, for example, if you have placed a marker to draw things. The length of the marker changes at what position the uArm will be touching the drawing surface.

To make scripting easier, you can set the position at which the uArm is level with the surface. This will then convert that position to `z=0`:

```python
robot = uarm_scan_and_connect()

robot.move_to(z=42)     # whatever height puts it level with the surface
robot.z_is_level()      # save the current height to be the zero position
robot.move_to(z=0)      # now this will be level with the surface (same as above)
```

## Wrist Offset

Sometimes the servo motor that rotates the uArms "wrist" is not centered. This might be able to be fixed by physically forcing it to skip some gears and realign with the center, however this risks damaging the motor.

You can save the servo motor's position when you see that it is centered:

```python
robot = uarm_scan_and_connect()

robot.rotate_to(102)        # whatever angle puts it in the center
robot.wrist_is_centered()   # save the current rotation to be the "center"
robot.rotate_to(90)         # now this will be centered (same as above)
```

## OpenMV Camera

The OpenMV camera has a few sources of innacuracy when attached to a uArm:

1. It can move around while mounted, because just 1 screw is holding it in place
2. The OpenMV lenses seem to all have different curvature
3. The enslosure uArm puts the OpenMV camera in is 3D printed and often warped

To help make the camera more accurately aligned with the uArm, a calibration process was developed.

#### Setup the OpenMV Camera

This process only works if an OpenMV camera has been attached to the uArm so that it is horizontal and facing downwards

The OpenMV script for calibration can be [found in the example folder](./examples/openmv/calibration.py). This script will print out data to the serial port, so you will need to select **`Tools -> Save open script to OpenMV Cam (main.py)`**

After saving the script and waiting a few seconds for it to fully flash, unplug and replug the OpenMV camera into your computer to restart it.

#### Setup the uArm

The script relies on the uArm having it's suction nozzle attached, so that it can operate in its `"general"` mode.

#### Setup the Calibration Image

Using a printer and normal printer paper, print the [calibration image from the examples folder](./examples/openmv/calibration.pdf).

Place the paper underneath the uArm, so that the uArm's base aligns with the picture.

#### Execute the Calibration Script

With both the uArm and OpenMV connected to your computer over USB, run the calibration script:

```bash
python -m uarm.openmv.calibrate
```

If you wish to save the OpenMV calibration to a custom location, pass the directory as an argument (this can be both relative or absolute path):
```bash
python -m uarm.openmv.calibrate ./path/to/my/directory
```

#### Run the Calibration Script

First, the uArm will home.

Second, the motors will turn off, and it will tell you:

```
"Place nozzle on center of calibration dots, and press ENTER"
```

When you see this, use your hand to carefully move the uArms nozzle so that it is resting on the calibration image. Try to have the nozzle as **perfectly centered with the 5 black circles** as you can.

Press `ENTER` key when you are ready.

The uArm will raise up to two positions, reading in the 5 circles' positions from the camera.

When it is done, it will save the calibration data to the `.hardware_settings` folder


