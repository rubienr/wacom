# Yet another Wacom Tool

Since the Ubuntu Wacom UI config behaves flaky I decided to do it on my own, relying only on command line and xsetwacom.
The script will not only work  Ubuntu but most probably also on a stone-age CentOS.
All it needs is

* xsetwacom - mandatory
* xbindkeys - optional: only if you intend to map mouse events to scripts
  * xdotool - optional: only if you intend to map mouse events to keyboard events (without "xsetwacom set NN Button key ...")
* xrandr - mandatory

## Aims
* simple
* stable
* reliable
* painless setup

## Non Aims
* fancy GUI
* autoconfig

# Usage

I tested this script on Ubuntu with Intuos BT M.
If your device is connected by USB, the Intuos BT M needs to be switched to Descktop Mode.
Wiht bluetooth it works out of the box.
Plese consult the Notes section for information about the modes.

## Examples

If your Intuos BT M device is connected by USB press the **leftmost + rightmost button simultaneously** until the white LED goes off and on agian (dim white).
Probably this step is not necessary for other devices.

    xsetwacom.sh --config krita                    # configure device
    xsetwacom.sh --config krita --xbindkeys daemon # start key mapping in background: 
                                                   #   button 3 maps device to primary screen
                                                   #   button 4 maps device to secondary screen

    # other examples
    xsetwacom.sh                    # read default config values and configure the device
    xsetwacom.sh --map primary      # map the pad to the primary monitor
    xsetwacom.sh --mode Absolute    # use absolute cursor
    xsetwacom.sh --parameters       # print supported parameters and exit

## Synopsis
    $ xsetwacom.sh --help
    Usage: xsetwacom.sh [OPTION ...] 

    Without command line arguments the script loads the default conguration and applies the parameters to attached device(s).
    Note: always specify --config as first prameter (even for --help).

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
                            primary   = 2048x1280+0+0
                            secondary = 2048x1280+2048+0
                            whole     = 4096x1280+0+0
                            next      = next geometry (cycles through all geometries)
                          Default: 4096x1280+0+0
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

## Full Example - Device Setup

    $ ./xsetwacom.sh --config krita
    Found devices:
      Wacom Intuos BT M Pad pad             id: 8   type: PAD
      Wacom Intuos BT M Pen stylus          id: 15  type: STYLUS
    Configuration "krita" loaded:
      PAD_DEVICE_IDS = "8"
      STYLUS_DEVICE_IDS = "15"
      ERASER_DEVICE_IDS = ""
      XBINDKEYS_CFG = ""
      ALL_PARAMETERS (3)
        [PressureCurve] = "0 0 50 70"
        [Mode] = "Absolute"
        [MapToOutput] = "2048x1280+0+0"
      PAD_PARAMETERS (0)
      PAD_BUTTON_MAPPING (4)
        [Button 8] = "14"
        [Button 1] = "key b"
        [Button 3] = "13"
        [Button 2] = "key t"
      STYLUS_PARAMETERS (0)
      STYLUS_BUTTON_MAPPING (2)
        [Button 1] = "0"
        [Button 2] = "0"
      ERASER_PARAMETERS (0)
      ERASER_BUTTON_MAPPING (0)
    Configure devices: 8 15
      Configure pad device 8
        Configure device 8 with ALL_PARAMETERS (3)
            PressureCurve = "0 0 50 70"
                    Property 'Wacom Pressurecurve' does not exist on device.
            Mode = "Absolute"
            MapToOutput = "2048x1280+0+0"
        Configure device 8 with PAD_PARAMETERS (0)
        Configure device 8 with PAD_BUTTON_MAPPING (4)
            Button 8 = "14"
            Button 1 = "key b"
            Button 3 = "13"
            Button 2 = "key t"
      Configure pen device 15
        Configure device 15 with ALL_PARAMETERS (3)
            PressureCurve = "0 0 50 70"
            Mode = "Absolute"
            MapToOutput = "2048x1280+0+0"
        Configure device 15 with STYLUS_PARAMETERS (0)
        Configure device 15 with STYLUS_BUTTON_MAPPING (2)
            Button 1 = "0"
            Button 2 = "0"
    Current device settings:
      Device 8 parameters
        xsetwacom set "8" "Button" "1" "key +b -b "
        xsetwacom set "8" "Button" "2" "key +t -t "
        xsetwacom set "8" "Button" "3" "button +13 "
        xsetwacom set "8" "Button" "8" "button +14 "
        xsetwacom set "8" "ToolDebugLevel" "0"
        xsetwacom set "8" "TabletDebugLevel" "0"
        xsetwacom set "8" "Suppress" "2"
        xsetwacom set "8" "RawSample" "4"
        xsetwacom set "8" "Mode" "Absolute"
        xsetwacom set "8" "Touch" "off"
        xsetwacom set "8" "Gesture" "off"
        xsetwacom set "8" "ZoomDistance" "0"
        xsetwacom set "8" "ScrollDistance" "0"
        xsetwacom set "8" "TapTime" "250"
        xsetwacom set "8" "RelWheelUp" "1" "button +5 "
        xsetwacom set "8" "RelWheelDown" "2" "button +4 "
        xsetwacom set "8" "AbsWheelUp" "3" "button +4 "
        xsetwacom set "8" "AbsWheelDown" "4" "button +5 "
        xsetwacom set "8" "AbsWheel2Up" "5" "button +4 "
        xsetwacom set "8" "AbsWheel2Down" "6" "button +5 "
        xsetwacom set "8" "StripLeftUp" "1" "button +4 "
        xsetwacom set "8" "StripLeftDown" "2" "button +5 "
        xsetwacom set "8" "StripRightUp" "3" "button +4 "
        xsetwacom set "8" "StripRightDown" "4" "button +5 "
        xsetwacom set "8" "Threshold" "0"
        xsetwacom set "8" "BindToSerial" "0"
        xsetwacom set "8" "PanScrollThreshold" "13"
      Device 15 parameters
        xsetwacom set "15" "Area" "0 0 21600 13500"
        xsetwacom set "15" "Button" "1" "button +0 "
        xsetwacom set "15" "Button" "2" "button +0 "
        xsetwacom set "15" "Button" "3" "button +3 "
        xsetwacom set "15" "Button" "8" "button +8 "
        xsetwacom set "15" "ToolDebugLevel" "0"
        xsetwacom set "15" "TabletDebugLevel" "0"
        xsetwacom set "15" "Suppress" "2"
        xsetwacom set "15" "RawSample" "4"
        xsetwacom set "15" "PressureCurve" "0 0 50 70"
        xsetwacom set "15" "Mode" "Absolute"
        xsetwacom set "15" "TabletPCButton" "off"
        xsetwacom set "15" "Touch" "off"
        xsetwacom set "15" "Gesture" "off"
        xsetwacom set "15" "ZoomDistance" "0"
        xsetwacom set "15" "ScrollDistance" "0"
        xsetwacom set "15" "TapTime" "250"
        xsetwacom set "15" "CursorProximity" "30"
        xsetwacom set "15" "Rotate" "none"
        xsetwacom set "15" "Threshold" "26"
        xsetwacom set "15" "BindToSerial" "0"
        xsetwacom set "15" "PressureRecalibration" "on"
        xsetwacom set "15" "PanScrollThreshold" "1300"
    Device settings diff (old vs. new config):
        2,3c2,3
        < xsetwacom set "8" "Button" "1" "key +p -p "
        < xsetwacom set "8" "Button" "2" "key +x -x "
        ---
        > xsetwacom set "8" "Button" "1" "key +b -b "
        > xsetwacom set "8" "Button" "2" "key +t -t "
    
## Full Example - Bind Device Buttons to Script

    $ ./xsetwacom.sh --config krita --xbindkeys daemon
    bind keys with ./configs/krita-xbindkeys.cfg (running in background)
    $ # you can safely close this shell

# Notes

## Intuos Pro L

This device broadcasts two Bluetooth beacons:

1. BT IntuosPro L, and
2. LE IntuosPro L.

In case of frequent disconnects or no battery level being reported remove all stored connections and pair the deivce again.
First the LE then the BT connection:

1. long press on touch circle button -> pair the LE connection, then
2. long press on touch circle button -> pair the BT connection

## Intuos BT M

The four wheel modes according to the lit LED are supported (see configuration file).

This device can be connected in three ways:

* by Bletooth (LED lights blue)
* by USB
  * in Desktop Mode (LED lights bright white)
  * in Mobile Mode (LED lights dim white)

To switch the Intuos BT M in between both USB modes press the **leftmost + rightmost buttons simultaneously** for about four seconds until the white LED goes off.
For this the USB cable must be connected.
Unfortunately this step is poorly propagated and the last mode is not preserved or the mode is not detected correctly.
See: https://github.com/linuxwacom/xf86-input-wacom/wiki/Known-Issues#android-misdetect

1. connected by Bluetooth

       $ xsetwacom --list
       Wacom Intuos BT M Pad pad               id: 10  type: PAD
       Wacom Intuos BT M Pen stylus            id: 11  type: STYLUS

2. connectede by USB - Mobile Mode (default)

       $ xsetwacom --list
       Wacom Co.,Ltd. Intuos BT M stylus       id: 10  type: STYLUS
       Wacom Co.,Ltd. Intuos BT M eraser       id: 11  type: ERASER

3. connected by USB - Desktop Mode

       $ xsetwacom --list
       Wacom Intuos BT M Pad pad               id: 10  type: PAD
       Wacom Intuos BT M Pen stylus            id: 11  type: STYLUS
       Wacom Intuos BT M Pen eraser            id: 17  type: ERASER
       Wacom Intuos BT M Pen cursor            id: 18  type: CURSOR
