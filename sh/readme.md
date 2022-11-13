# Yet another Wacom Tool**NOTE: The shell script variant is not maintained anymore. For newer features use the Python implementation**

**NOTE: The shell script variant is not maintained anymore. For newer features use the Python implementation**  

Since the Wacom config UI in KDE Plasma and Gnome 2/3 perform very poor in defining a proper behaviour,
this scripting project aims to allow a more sophisticated way to configure a Wacom board.
It is based on `xsetwacom` and `XBindKeys`.
This tool also helps to visualize the pen pressure curve and the pen pressure (live plot) for adjustments.

**Examples**

This will read the `krita-intuous-pro` configs, run `xbindkeys` in backgruond and map one button to cycle through the screen mappings (left, right, both).
Additionally to cycling, it will trigger to reload the whole configuration from disk and set the device parameters with `xsetwacom`.

    $ ./xsetwacom.sh --config krita-intuous-pro --xbindkeys daemon
    bind keys with /home/.../krita-intuous-pro.cfg (running in background)

A one time configuration can be achieved as follows:

    $ ./xsetwacom.sh --config krita-intuous-pro

**Limitations**

- X11 only, no Wayland support
- no Gnome Shell support (github.com/linuxwacom/xf86-input-wacom/issues/289)


**Requirements**

- `xsetwacom` - mandatory
- `xbindkeys` - optional but recommended: triggers scripts on mouse events (button press), needed for wheel button (not all devices have this), automatic toggle mapped screen area (dual screen mode)
  - xdotool - optional: only if you intend to map mouse events to keyboard events (without "xsetwacom set NN Button key ...")
- `xrandr` - mandatory

**Aims**

- simple
- painless setup

**Non Aims**

- fancy GUI
- auto configuration

## Preparation Notes

### Intuos Pro L

This device broadcasts two Bluetooth beacons. Both connections need to be paired 'LE Intuous Pro L' and 'BT Intuous Pro L'.
In case of frequent disconnects or no battery level being reported remove both paired connections and pair the deivce again.
First pair the LE then the BT connection. Once paired, connecting only to BT is sufficient.

1. long press on touch circle button -> pair the LE connection, then
2. long press on touch circle button -> pair the BT connection

### Intuos BT M

This device can be connected in three ways:

- by Bletooth (LED lights blue)
- by USB
  - in Desktop Mode (LED lights bright white)
  - in Mobile Mode (LED lights dim white)
  
If the device is connected by USB, the Intuos BT M needs to be switched to Descktop Mode, by bluetooth it works out of the box.

To switch in between both USB modes press the **leftmost + rightmost buttons simultaneously** for about four seconds until the white LED goes off.
For this step the USB cable must be connected.
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
       

## Synopsis
    $ xsetwacom.sh --help
    Usage: xsetwacom.sh [OPTION ...] 

    Without command line arguments the script loads the default conguration and applies the parameters to attached device(s).
    Note: always specify --config as first prameter (even for --help).
    Note: gnome-shell is not supported. Most settings will work except emitting button events (see man xsetwacom "Button button-number [mapping]" in section PARAMETERS)
    Options:

      --parameters        Print all supported device parameters and exit.
      --configs           List all configuration names and exit.
      --print-config [<config-name>]
                          Print the configuration and exit.
                          config-name: see --configs.
                          Default: default.
      --help              Print this help.

      A few device arguments can be defined by command line. Any other must be defined in the configuration file.

      --config [<config-name>]
                          If specified always let this argument be the 1st on command line. Create your own configs in ./configs/.
                          config-name: see --configs.
                          Default: default.
      --map [primary|seconary|whole|next]
                          Map device to primary, secondary or all monitor(s) (as reported by xrandr).
                          xrandr reported geometries are:
                            primary   = 3840x2160+0+0
                            secondary = 3840x2160+3840+0
                            whole     = 7680x2160+0+0
                            next      = next geometry (cycles through all geometries)
      --mode [Absolute|Relative]
                          Absolute or relative pointer behaviour.
                          Default: Absolute

      Key binding manipulaton (see also xbindkeys manual).

      --xbindkeys [nodaemon|daemon|reload|kill]
                          Manipulate system key bindings and exit.
                            nodaemon: start xbindkeys with configuration krita-intuos-bt_xbindkeys.cfg in foreground
                            daemon:   start xbindkeys with configuration krita-intuos-bt_xbindkeys.cfg in background
                            reload:   tell xbindkeys to reaload the configuration
                            kill:     try to stop all xbindkeys instances
                          Default: nodaemon.

      Plot pressure cure.

      --curve
                          Plot the configured pressure curve and the resulting Bezier curve.
      --pressure
                          Live plot the current pressure curve (requires feedgnuplot). The pressure plot does not appear until the first pressure value is reported.
