import pprint
from enum import Enum
from typing import Dict, Union, Callable, Tuple


class DeviceConfigType(Enum):
    PAD = 1
    STYLUS = 2
    ERASER = 3
    CURSOR = 4
    TOUCH = 5
    ALL = 6


class DeviceParameter(object):
    def __init__(self):
        """
        Allowed parameter (`xsetwacom --list parameters`):
            Area                  - Valid tablet area in device coordinates.
            Button                - X11 event to which the given button should be mapped.
            ToolDebugLevel        - Level of debugging trace for individual tools (default is 0 [off]).
            TabletDebugLevel      - Level of debugging statements applied to shared code paths between all tools associated with the same tablet (default is 0 [off]).
            Suppress              - Number of points trimmed (default is 2).
            RawSample             - Number of raw data used to filter the points (default is 4).
            PressureCurve         - Bezier curve for pressure (default is 0 0 100 100 [linear]).
            Mode                  - Switches cursor movement mode (default is absolute).
            TabletPCButton        - Turns on/off Tablet PC buttons (default is off for regular tablets, on for Tablet PC).
            Touch                 - Turns on/off Touch events (default is on).
            HWTouchSwitchState    - Touch events turned on/off by hardware switch.
            Gesture               - Turns on/off multi-touch gesture events (default is on).
            ZoomDistance          - Minimum distance for a zoom gesture (default is 50).
            ScrollDistance        - Minimum motion before sending a scroll gesture (default is 20).
            TapTime               - Minimum time between taps for a right click (default is 250).
            CursorProximity       - Sets cursor distance for proximity-out in distance from the tablet (default is 10 for Intuos series, 42 for Graphire series).
            Rotate                - Sets the rotation of the tablet. Values = none, cw, ccw, half (default is none).
            RelWheelUp            - X11 event to which relative wheel up should be mapped.
            RelWheelDown          - X11 event to which relative wheel down should be mapped.
            AbsWheelUp            - X11 event to which absolute wheel up should be mapped.
            AbsWheelDown          - X11 event to which absolute wheel down should be mapped.
            AbsWheel2Up           - X11 event to which absolute wheel up should be mapped.
            AbsWheel2Down         - X11 event to which absolute wheel down should be mapped.
            StripLeftUp           - X11 event to which left strip up should be mapped.
            StripLeftDown         - X11 event to which left strip down should be mapped.
            StripRightUp          - X11 event to which right strip up should be mapped.
            StripRightDown        - X11 event to which right strip down should be mapped.
            Threshold             - Sets tip/eraser pressure threshold (default is 27).
            ResetArea             - Resets the bounding coordinates to default in tablet units.
            ToolType              - Returns the tool type of the associated device.
            ToolSerial            - Returns the serial number of the current device in proximity.
            ToolID                - Returns the tool ID of the current tool in proximity.
            ToolSerialPrevious    - Returns the serial number of the previous device in proximity.
            BindToSerial          - Binds this device to the serial number.
            TabletID              - Returns the tablet ID of the associated device.
            PressureRecalibration - Turns on/off Tablet pressure recalibration
            PanScrollThreshold    - Adjusts distance required for pan actions to generate a scroll event
            MapToOutput           - Map the device to the given output.
        """

        self.args: Dict[str, Union[str, Callable[[], str]]] = {}


class BaseConfig(object):

    def __init__(self):
        self.device_hint_expression: str = ""  # i.e. regex ".*Wacom Intuos Pro.*"
        self.devices: Dict[DeviceConfigType: DeviceParameter] = {}
        self.xbindkeys_config_string = ""
        """
        Example:
        
        .. code-block:: bash 
           # bind button 12 to toggle screens
           "./xsetwacom.py --config krita-intuos-pro --map next"
           b:12
           # bind wheel button to toggle the wheel mode
           "./xsetwacom.py --config krita-intuos-pro"
           b:10
        """

        self.pressure_curve: \
            Dict[DeviceConfigType,  # stylus or eraser
                 Tuple[  # bezier in-between (0,0), p1, p2, (100,100) for each pressure device
                     Tuple[int, int],  # p1
                     Tuple[int, int],  # p2
                 ]] = {}

    def print_config(self):
        p = pprint.PrettyPrinter(indent=4, compact=True)
        p.pprint({"device_hint": self.device_hint_expression,
                  "devices": self.devices,
                  "xbindkeys": self.xbindkeys_config_string,
                  "pressure_curve": self.pressure_curve,
                  })
