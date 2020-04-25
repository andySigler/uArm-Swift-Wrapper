# Record

This module uses the uArm's absolute-position rotary encoders to record user-made motions while the motors are disabled. This makes it potentially much easier to orchestrate multiple complicated movements within a script, and removes the need to design movements point-by-point.

### Recording Tool

This module comes with a script to make it easier to record movements. The script is ran like:

```bash
python -m uarm.record <RECODING-NAME>
```

Where `<RECORDING-NAME>` is a unique name that the recording will be saved under. For example, I could create a recording called `"my-test-recording"` by running:

```bash
python -m uarm.record my-test-recording
```

#### Save Location

By default, recordings are saved in the `SwiftAPIWrapper`'s default `.hardware_settings` folder. Currently, this is being set as the location of the `uarm` Python modules installation.

However, it is very useful to store both `.hardware_settings` and recordings within a project's directory, to clearly separate configurations and recordings between different applications.

To set the location of where the recording is stored, pass the `--dir` option to the script:

```bash
python -m uarm.record my-test-recording --dir .
```

The above will save it to the current folder where the command is being ran. You can also pass an explicit path:

```bash
python -m uarm.record my-test-recording --dir /path/to/save/directory
```

#### Recording Method

Currently, the recording to has two methods for save new uArm positions:

1. Automatically recording new positions as fast as possible
2. Recording a the current position when the `ENTER` key is pressed on the keyboard

By default, the `uarm.record` tool will use option number 2, where a new uArm position is recording each time the `ENTER` key is pressed on the user's keyboard.

If, however, you wish to automatically record all positions as fast as possible, you can pass the `--auto` option to the tool:

```bash
python -m uarm.record my-test-recording --auto
```

When `--auto` is enabled, the recording tool will begin saving positions once the uArm is moved, and stop recording once the uArm has been still for 1 second.

#### Playback After

The recording that was just made can be testing by replying `yes` or `y` to the prompt at the end of the script. If yes, then the new recording will immediately be played back using the uArm's default speed setting.

If the `--auto` option was used during record, then the speed is determined by the speed that the uArm was moved during recording. Also, if `--auto` option was used, then you have the additional option to "filter" out repetitive positions to make the movement smoother (this feature is still buggy).
