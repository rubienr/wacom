import re
from typing import Dict, Union, Callable, Tuple

CONFIG_FILE_MODULE_SUFFIX: str = "_config"
PY_CONFIG_FILE_SUFFIX: str = f"{CONFIG_FILE_MODULE_SUFFIX}.py"


class DeviceParameters(object):
    def __init__(self,
                 args: Dict[str,  # parameter
                            Union[
                                Tuple[str, str],  # value, description text
                                Callable[[], Tuple[str, str]]  # call-able -> value, description text
                            ]]) -> None:
        self.known_args: Dict[str, str] = {
            # Allowed parameter (`xsetwacom --list parameters`):
            "Area": "Valid tablet area in device coordinates.",
            r"Button [\d]+": "X11 event to which the given button should be mapped.",
            "ToolDebugLevel": "Level of debugging trace for individual tools (default is 0 [off]).",
            "TabletDebugLevel": "Level of debugging statements applied to shared code paths between all tools associated with the same tablet (default is 0 [off]).",
            "Suppress": "Number of points trimmed (default is 2).",
            "RawSample": "Number of raw data used to filter the points (default is 4).",
            "PressureCurve": "Bezier curve for pressure (default is 0 0 100 100 [linear]).",
            "Mode": "Switches cursor movement mode (default is absolute).",
            "TabletPCButton": "Turns on/off Tablet PC buttons (default is off for regular tablets, on for Tablet PC).",
            "Touch": "Turns on/off Touch events (default is on).",
            "HWTouchSwitchState": "Touch events turned on/off by hardware switch.",
            "Gesture": "Turns on/off multi-touch gesture events (default is on).",
            "ZoomDistance": "Minimum distance for a zoom gesture (default is 50).",
            "ScrollDistance": "Minimum motion before sending a scroll gesture (default is 20).",
            "TapTime": "Minimum time between taps for a right click (default is 250).",
            "CursorProximity": "Sets cursor distance for proximity-out in distance from the tablet (default is 10 for Intuos series, 42 for Graphire series).",
            "Rotate": "Sets the rotation of the tablet. Values = none, cw, ccw, half (default is none).",
            "RelWheelUp": "X11 event to which relative wheel up should be mapped.",
            "RelWheelDown": "X11 event to which relative wheel down should be mapped.",
            "AbsWheelUp": "X11 event to which absolute wheel up should be mapped.",
            "AbsWheelDown": "X11 event to which absolute wheel down should be mapped.",
            "AbsWheel2Up": "X11 event to which absolute wheel up should be mapped.",
            "AbsWheel2Down": "X11 event to which absolute wheel down should be mapped.",
            "StripLeftUp": "X11 event to which left strip up should be mapped.",
            "StripLeftDown": "X11 event to which left strip down should be mapped.",
            "StripRightUp": "X11 event to which right strip up should be mapped.",
            "StripRightDown": "X11 event to which right strip down should be mapped.",
            "Threshold": "Sets tip/eraser pressure threshold (default is 27).",
            "ResetArea": "Resets the bounding coordinates to default in tablet units.",
            "ToolType": "Returns the tool type of the associated device.",
            "ToolSerial": "Returns the serial number of the current device in proximity.",
            "ToolID": "Returns the tool ID of the current tool in proximity.",
            "ToolSerialPrevious": "Returns the serial number of the previous device in proximity.",
            "BindToSerial": "Binds this device to the serial number.",
            "TabletID": "Returns the tablet ID of the associated device.",
            "PressureRecalibration": "Turns on/off Tablet pressure recalibration",
            "PanScrollThreshold": "Adjusts distance required for pan actions to generate a scroll event",
            "MapToOutput": "Map the device to the given output.",
        }
        self._args: Dict[str, Union[Tuple[str, str], Callable[[], Tuple[str, str]]]] = {}
        self.args = args

    @property
    def args(self) -> Dict[str, Union[Tuple[str, str], Callable[[], Tuple[str, str]]]]:
        return self._args

    @args.setter
    def args(self, value: Dict[str, Union[Tuple[str, str], Callable[[], Tuple[str, str]]]]) -> None:
        for arg in value.keys():
            if not any([re.match(known_arg, arg) for known_arg in self.known_args.keys()]):
                print(f"WARNING: unknown argument '{arg}' detected")
        self._args = value
