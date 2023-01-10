import os
from enum import Enum
from typing import Dict, Tuple

from src.config.BaseConfig import BaseConfig
from src.config.BaseConfig import DeviceParameters
from src.geometry.types import Point, InputArea
from src.wacom.DeviceTypeName import DeviceTypeName
from src.wacom.get import get_active_led_number_once


class TouchRingMode(Enum):
    ONE = 1  # top left indicator LED
    TWO = 2  # top right indicator LED
    THREE = 3  # bottom right indicator LED
    FOUR = 0  # bottom left indicator LED
    UNDEFINED = 99


class Config(BaseConfig):
    def __init__(self) -> None:
        super().__init__(file_path_name=__file__)
        self.device_hint_expression: str = r"^Wacom Intuos Pro .*"
        self.device_input_areas: Dict[DeviceTypeName, InputArea] = {
            DeviceTypeName.STYLUS: InputArea(Point(0, 0), Point(62200, 43200)),
            DeviceTypeName.ERASER: InputArea(Point(0, 0), Point(62200, 43200)),
            DeviceTypeName.TOUCH: InputArea(Point(0, 0), Point(12400, 8640))
        }
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
                    "Button 13": ("button 13", "toggle modes"),  # leave default in order to work with xbindkeys without prior configuration by `xsetwacom --config <cfg> configure device --set`

                    # ↓ 5th button
                    "Button 9": ("key KP_1", "front view"),
                    "Button 10": ("key KP_1 key KP_Separator key Home", "front view, center selected, frame all"),
                    "Button 11": ("key q", "quick favourites"),
                    "Button 12": ("button 12", "map to next screen"),  # leave default in order to work with xbindkeys without prior configuration by `xsetwacom --config <cfg> configure device --set`
                    # ↑ bottom button

                    "AbsWheelUp": lambda: ConfigHelper.get_abs_wheel_up_mode(self.device_hint_expression),  # call-able retrieving the corresponding mode according to the touch-ring LED state
                    "AbsWheelDown": lambda: ConfigHelper.get_abs_wheel_down_mode(self.device_hint_expression),  # call-able retrieving the corresponding mode according to the touch-ring LED state
                }),
            DeviceTypeName.STYLUS: DeviceParameters({
                "Mode": ("Absolute", "absolute mode pointer device"),
                "PressureCurve": ("40 0 40 100", "stylus pressure curve"),
            }),
            DeviceTypeName.ERASER: DeviceParameters({
                "Mode": ("Absolute", "absolute mode pointer device"),
                "PressureCurve": ("0 0 50 70", "eraser pressure curve"),
            }),
        }

        self.xbindkeys_config_string = f"""
# bind button 12 to toggle screens/geometry
"{os.path.join(BaseConfig.root_path_from_abs_filepath(__file__), "xsetwacom.py")} --log DEBUG --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --map keep"
b:12

# bind the wheel button to trigger a complete re-configuration of the pad depending on the LEDs state
"{os.path.join(BaseConfig.root_path_from_abs_filepath(__file__), "xsetwacom.py")} --log DEBUG --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --set"
b:13
"""


class ConfigHelper:

    @staticmethod
    def get_abs_wheel_up_mode(device_hint_expression: str) -> Tuple[str, str]:
        """
        Wheel modes when turning wheel left.
        :return: key sequence (see man xsetwacom)
        """
        return {
            TouchRingMode.ONE: ("key +shift KP_4", "roll/rotate right"),
            TouchRingMode.TWO: ("key +KP_Add", "zoom in"),
            TouchRingMode.THREE: ("key left", "previous frame"),
            TouchRingMode.FOUR: ("key Down", "previous key frame"),
            TouchRingMode.UNDEFINED: ("", "in case device is not connected"),
        }[TouchRingMode(get_active_led_number_once(device_hint_expression, default_on_error=TouchRingMode.UNDEFINED.value))]

    @staticmethod
    def get_abs_wheel_down_mode(device_hint_expression: str) -> Tuple[str, str]:
        """
        Wheel modes when turning wheel right.
        :return: key sequence (see man xsetwacom)
        """
        return {
            TouchRingMode.ONE: ("key +shift KP_6", "roll/rotate left"),
            TouchRingMode.TWO: ("key +KP_Subtract", "zoom out"),
            TouchRingMode.THREE: ("key Right", "next frame"),
            TouchRingMode.FOUR: ("key Up", "next key frame"),
            TouchRingMode.UNDEFINED: ("", "in case device is not connected"),
        }[TouchRingMode(get_active_led_number_once(device_hint_expression, default_on_error=TouchRingMode.UNDEFINED.value))]
