from enum import Enum
from typing import Dict, Tuple

from src.DeviceTypeName import DeviceTypeName
from src.base_config import BaseConfig
from src.base_config import DeviceParameters
from src.geometry_types import Point, InputArea
from src.tablet_utils import get_led_on_off_state


class TouchRingMode(Enum):
    ONE = 1  # top left indicator LED
    TWO = 2  # top right indicator LED
    THREE = 3  # bottom right indicator LED
    FOUR = 0  # bottom left indicator LED
    UNDEFINED = 99


class Config(BaseConfig):
    def __init__(self):
        super().__init__()
        self.device_hint_expression: str = ".*Wacom Intuos Pro.*"
        self.device_input_area: InputArea = InputArea(Point(0, 0), Point(62200, 43200))
        self.devices_parameters: Dict[DeviceTypeName, DeviceParameters] = {
            DeviceTypeName.PAD:
                DeviceParameters({
                    "Mode": ("Absolute", "absolute mode pointer device"),
                    # ↓ top button
                    "Button 1": ("key +ctrl z", "undo"),
                    "Button 2": ("key shift", "Shift"),
                    "Button 3": ("key ctrl", "Control"),
                    "Button 8": ("key f", "tool radius, tool strength: Shift + f, tool angle: Control + f"),
                    # ↑ 4th button
                    # ↓ touch ring button
                    "Button 13": ("button 13", "toggle modes"), # leave default in order to work with xbindkeys without prior configuration by `xsetwacom --config <cfg> configure device --set`
                    # ↓ 5th button
                    "Button 9": ("key KP_1", "front view"),
                    "Button 10": ("key KP_1 key KP_Separator key Home", "front view, center selected, frame all"),
                    "Button 11": ("key q", "quick favourites"),
                    "Button 12": ("button 12", "map to next screen"), # leave default in order to work with xbindkeys without prior configuration by `xsetwacom --config <cfg> configure device --set`
                    # ↑ bottom button
                    "AbsWheelUp": Config.get_abs_wheel_up_mode,  # call-able retrieving the corresponding mode according to the touch-ring LED state
                    "AbsWheelDown": Config.get_abs_wheel_down_mode,  # call-able retrieving the corresponding mode according to the touch-ring LED state
                }),
            DeviceTypeName.STYLUS: DeviceParameters({
                "PressureCurve": ("40 0 40 100", "stylus pressure curve"),
            }),
            DeviceTypeName.ERASER: DeviceParameters({
                "PressureCurve": ("0 0 50 70", "eraser pressure curve"),
            }),
        }

        self.xbindkeys_config_string = f"""
# bind button 12 to toggle screens/geometry
"./xsetwacom.py --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --map
b:12

# bind the wheel button to toggle a complete re-configuration of the pad depending on the LEDs state
"./xsetwacom.py --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --set"
b:13
"""

    @staticmethod
    def get_abs_wheel_up_mode() -> Tuple[str, str]:
        """
        Wheel modes when turning/sliding left.
        :return: key sequence (see man xsetwacom)
        """
        return {
            TouchRingMode.ONE: ("key +shift KP_4", "roll/rotate right"),
            TouchRingMode.TWO: ("key +KP_Add", "zoom in"),
            TouchRingMode.THREE: ("key left", "previous frame"),
            TouchRingMode.FOUR: ("key Down", "previous key frame"),
            TouchRingMode.UNDEFINED: ("", "in case device is not connected"),
        }[Config._get_touch_ring_mode()]

    @staticmethod
    def get_abs_wheel_down_mode() -> Tuple[str, str]:
        """
        Wheel modes when turning/sliding right.
        :return: key sequence (see man xsetwacom)
        """
        return {
            TouchRingMode.ONE: ("key +shift KP_6", "roll/rotate left"),
            TouchRingMode.TWO: ("key +KP_Subtract", "zoom out"),
            TouchRingMode.THREE: ("key Right", "next frame"),
            TouchRingMode.FOUR: ("key Up", "next key frame"),
            TouchRingMode.UNDEFINED: ("", "in case device is not connected"),
        }[Config._get_touch_ring_mode()]

    @staticmethod
    def _get_touch_ring_mode() -> TouchRingMode:
        """
        :return: First touch-ring LED found to be on.
        """
        states: Dict[int, bool] = get_led_on_off_state()
        for led_nr, is_on in states.items():
            if is_on:
                return TouchRingMode(int(led_nr))
        return TouchRingMode.UNDEFINED
