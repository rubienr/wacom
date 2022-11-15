# Yet another Wacom Tool

Since the Wacom config UI in KDE Plasma and Gnome 2/3 is very limiting performs poor in defining a proper behaviour, this project aims to painlessly allow achieving a sophisticated Wacom board
behaivour. It is based on `xsetwacom` and `XBindKeys`. This tool also helps to visualize the pressure curve and the current pressure (live plot).

## Examples

```bash
# in most cases, if the configuration is set up correctly, 
# this is enough:
$ ./xsetwacom.py --config <your_config> bindkeys --start
# xbindkeys will react on screen toggle (i.e. the bottom most button), 
# and on mode switch (i.e. wheel button). 
# This will trigger the re-configuration of either the input area or the wheel mode.
```

```bash
# one time configuration: load configuration and set device parameters
$ ./xsetwacom.py --config <your_config> device --set
# if screen toggle and mode switch is not desired, this command is enough
```

## Limitations

- X11 only, no Wayland support
- no Gnome Shell support (github.com/linuxwacom/xf86-input-wacom/issues/289)

## Requirements

- `xsetwacom` - mandatory
- `xbindkeys` - optional but recommended: triggers scripts on mouse events (button press), needed for wheel button (not all devices have this), automatic toggle mapped screen area (dual screen mode)
    - xdotool - optional: only if you intend to map mouse events to keyboard events (without "xsetwacom set NN Button key ...")
- `xrandr` - mandatory

## Aims and Non Aims

- \+ simple
- \+ painless setup
- \+ allow sophisticated setup
- \- no fancy GUI
- \- no auto configuration

## Synopsis

```bash
$ ./xsetwacom.py --help
usage: xsetwacom.py [-h] [-c {krita_intuos_pro}] {device,bindkeys,config,plot} ...

options:
  -h, --help            show this help message and exit

command (required):
  Run command with the loaded configuration.

  {device,bindkeys,config,plot}
    device              detect devices; set and get device parameter
    bindkeys            bind device-key events to system mouse/keyboard events
    config              print known configurations or configuration values
    plot                Visualize pressure curve or current pressure.

Configuration:
  Load and provide the configuration to the command.

  -c {krita_intuos_pro}, --config {krita_intuos_pro}
                        Loads the given configuration by name. (default: krita_intuos_pro)
```

# Device Notes

## Intuos Pro L

This device broadcasts two Bluetooth beacons. Both connections need to be paired 'LE Intuous Pro L' and 'BT Intuous Pro L'. In case of frequent disconnects or no battery level being reported remove
both paired connections and pair the deivce again. First pair the LE then the BT connection. Once paired, connecting only to BT is sufficient.

1. long press on touch circle button -> pair the LE connection, then
2. long press on touch circle button -> pair the BT connection

## Intuos BT M

This device can be connected in three ways:

- by Bletooth (LED lights blue)
- by USB
    - in Desktop Mode (LED lights bright white)
    - in Mobile Mode (LED lights dim white)

If the device is connected by USB, the Intuos BT M needs to be switched to Descktop Mode, by bluetooth it works out of the box.

To switch in between both USB modes press the **leftmost + rightmost buttons simultaneously** for about four seconds until the white LED goes off. For this step the USB cable must be connected.
Unfortunately this step is poorly propagated and the last mode is not preserved or the mode is not detected correctly.
See: https://github.com/linuxwacom/xf86-input-wacom/wiki/Known-Issues#android-misdetect

Device detected if connected by:

1. Bluetooth

       $ xsetwacom --list
       Wacom Intuos BT M Pad pad               id: 10  type: PAD
       Wacom Intuos BT M Pen stylus            id: 11  type: STYLUS

2. USB - Mobile Mode (default)

       $ xsetwacom --list
       Wacom Co.,Ltd. Intuos BT M stylus       id: 10  type: STYLUS
       Wacom Co.,Ltd. Intuos BT M eraser       id: 11  type: ERASER

3. USB - Desktop Mode

       $ xsetwacom --list
       Wacom Intuos BT M Pad pad               id: 10  type: PAD
       Wacom Intuos BT M Pen stylus            id: 11  type: STYLUS
       Wacom Intuos BT M Pen eraser            id: 17  type: ERASER
       Wacom Intuos BT M Pen cursor            id: 18  type: CURSOR
