# Yet another Wacom Tool

Since the Ubuntu Wacom UI config behaves flaky I decided to do it on my own, relying ony command line and xsetwacom.
The script will not only work  Ubuntu.
All it needs is

* xsetwacom
* optinally: xbindkeys
* optionally: xdotool

## Aims
* simple
* stable
* reliable

## Non Aims
* fancy GUI
* autoconfig

# Usage

## Examples

    xsetwacom.sh                    # read all values from config and configure to device
    xsetwacom.sh --map primary      # map the pad to the primary monitor
    xsetwacom.sh --curve 0 0 50 70  # set the pressure curve
    xsetwacom.sh --mode Absolute    # use absolute cursor
    xsetwacom.sh --parameters       # print supported parameters and exit
    xsetwacom.sh --map primary --config mypaint --mode Absolute

## Synopsis
    $ ./xsetwacom.sh --help

    Usage: xsetwacom.sh [OPTION ...] 

     Options:
      --help              Print this help.
      --map [primary|seconary|whole]
                          Map to primary secondary or all monitor(s) (as reported by xrandr).
                          Current geometries are:
                            primary   = 2048x1280+0+0
                            secondary = 2048x1280+2048+0
                            whole     = 4096x1280+0+0
                          Default: 2048x1280+0+0
      --mode              Absolute or Relative behaviour.
                          Default: Absolute
      --curve [x1 y1 x2 y2]
                          Set the pressure curve (3rd oder Bezier)
                          Default: 0 0 50 70
      --config [default|gimp|krita|mypaint]
                          Create your own configs in ./configs/.
                          Default: default.
      --parameters        Print all device parameters and exit.


## Full Example
    $ xsetwacom.sh 
    Found devices:
      Wacom Intuos BT M Pen stylus          id: 8   type: STYLUS
      Wacom Intuos BT M Pad pad             id: 15  type: PAD
    Configuration "default" loaded:
      PAD_DEVICE_IDS = "15"
      STYLUS_DEVICE_IDS = "8"
      ERASER_DEVICE_IDS = ""
      XBINDKEYS_CFG = "default-xbindkeys.cfg"
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
    Configure devices:
      Configure pad device 15
        Configure device 15 with ALL_PARAMETERS
        Configure device 15 with PAD_PARAMETERS
        Configure device 15 with PAD_BUTTON_MAPPING
      Configure pen device 8
        Configure device 8 with ALL_PARAMETERS
        Configure device 8 with STYLUS_PARAMETERS
        Configure device 8 with STYLUS_BUTTON_MAPPING
    Current device settings:
      Device 8 parameters
        xsetwacom set "8" "Area" "0 0 21600 13500"
        xsetwacom set "8" "Button" "1" "button +1 "
        xsetwacom set "8" "Button" "2" "button +2 "
        xsetwacom set "8" "Button" "3" "button +3 "
        xsetwacom set "8" "Button" "8" "button +8 "
        xsetwacom set "8" "ToolDebugLevel" "0"
        xsetwacom set "8" "TabletDebugLevel" "0"
        xsetwacom set "8" "Suppress" "2"
        xsetwacom set "8" "RawSample" "4"
        xsetwacom set "8" "PressureCurve" "0 0 100 100"
        xsetwacom set "8" "Mode" "Absolute"
        xsetwacom set "8" "TabletPCButton" "off"
        xsetwacom set "8" "Touch" "off"
        xsetwacom set "8" "Gesture" "off"
        xsetwacom set "8" "ZoomDistance" "0"
        xsetwacom set "8" "ScrollDistance" "0"
        xsetwacom set "8" "TapTime" "250"
        xsetwacom set "8" "CursorProximity" "30"
        xsetwacom set "8" "Rotate" "none"
        xsetwacom set "8" "Threshold" "26"
        xsetwacom set "8" "BindToSerial" "0"
        xsetwacom set "8" "PressureRecalibration" "on"
        xsetwacom set "8" "PanScrollThreshold" "1300"
      Device 15 parameters
        xsetwacom set "15" "Button" "1" "button +1 "
        xsetwacom set "15" "Button" "2" "button +2 "
        xsetwacom set "15" "Button" "3" "button +3 "
        xsetwacom set "15" "Button" "8" "button +8 "
        xsetwacom set "15" "ToolDebugLevel" "0"
        xsetwacom set "15" "TabletDebugLevel" "0"
        xsetwacom set "15" "Suppress" "2"
        xsetwacom set "15" "RawSample" "4"
        xsetwacom set "15" "Mode" "Absolute"
        xsetwacom set "15" "Touch" "off"
        xsetwacom set "15" "Gesture" "off"
        xsetwacom set "15" "ZoomDistance" "0"
        xsetwacom set "15" "ScrollDistance" "0"
        xsetwacom set "15" "TapTime" "250"
        xsetwacom set "15" "RelWheelUp" "1" "button +5 "
        xsetwacom set "15" "RelWheelDown" "2" "button +4 "
        xsetwacom set "15" "AbsWheelUp" "3" "button +4 "
        xsetwacom set "15" "AbsWheelDown" "4" "button +5 "
        xsetwacom set "15" "AbsWheel2Up" "5" "button +4 "
        xsetwacom set "15" "AbsWheel2Down" "6" "button +5 "
        xsetwacom set "15" "StripLeftUp" "1" "button +4 "
        xsetwacom set "15" "StripLeftDown" "2" "button +5 "
        xsetwacom set "15" "StripRightUp" "3" "button +4 "
        xsetwacom set "15" "StripRightDown" "4" "button +5 "
        xsetwacom set "15" "Threshold" "0"
        xsetwacom set "15" "BindToSerial" "0"
        xsetwacom set "15" "PanScrollThreshold" "13"
    Device settings diff (old vs. new config):
      xsetwacom reported no changes
