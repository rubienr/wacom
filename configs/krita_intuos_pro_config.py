from enum import Enum
from typing import Dict

from src.DeviceTypeName import DeviceTypeName
from src.base_config import BaseConfig
from src.base_config import DeviceParameters
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
        self.devices_parameters: Dict[DeviceTypeName: DeviceParameters] = {
            DeviceTypeName.PAD:
                DeviceParameters({
                    "Mode": "Absolute",
                    # ↓ top button
                    "Button 1": "key +ctrl z",  # undo
                    "Button 2": "key shift",  # Shift
                    "Button 3": "key ctrl",  # Control
                    "Button 8": "key +ctrl +alt 1",  # swap with last tool
                    # ↑ 4th button
                    # ↓ touch ring button
                    "Button 13": "button 10",  # toggle modes
                    # ↓ 5th button
                    "Button 9": "key e",  # toggle brush mode: normal/erase
                    "Button 10": "key 5 2",  # reset zoom + rotation
                    "Button 11": "key r",  # reset tool
                    "Button 12": "button 12",  # map to next screen
                    # ↑ bottom button
                    "AbsWheelUp": Config.get_abs_wheel_up_mode,  # call-able retrieving the corresponding mode according to the touch-ring LED state
                    "AbsWheelDown": Config.get_abs_wheel_down_mode,  # call-able retrieving the corresponding mode according to the touch-ring LED state
                }),
            DeviceTypeName.STYLUS: DeviceParameters({
                "PressureCurve": "70 0 70 100",
            }),
            DeviceTypeName.ERASER: DeviceParameters({
                "PressureCurve": "0 0 50 70",
            }),
        }

        self.wheel_modes = {
            "AbsWheelUp": {  # turn left
                TouchRingMode.ONE: "key 4",  # rotate
                TouchRingMode.TWO: "key +plus",  # zoom
                TouchRingMode.THREE: "key +altgr 8 key +altgr 8 key +altgr 8",  # increase brush size
                TouchRingMode.FOUR: "key I",  # increase opacity
            },
            "AbsWheelDown": {  # turn right
                TouchRingMode.ONE: "key 6",  # rotate
                TouchRingMode.TWO: "key +minus",  # zoom
                TouchRingMode.THREE: "key +altgr 9 key +altgr 9 key +altgr 9",  # decrease brush size
                TouchRingMode.FOUR: "key O",  # decrease opacity
            }
        }

        self.xbindkeys_config_string = f"""
# bind button 12 to toggle screens/geometry
"./xsetwacom.py --xsetwacom --config {BaseConfig.config_name_from_abs_filepath(__file__)} --map next"
b:12

# bind the wheel button to toggle a complete re-configuration of the pad depending on the LEDs state
"./xsetwacom.py --xsetwacom --config {BaseConfig.config_name_from_abs_filepath(__file__)}"
b:10
"""

    @staticmethod
    def get_abs_wheel_up_mode() -> str:
        """
        Wheel modes when turning/sliding left.
        :return: key sequence (see man xsetwacom)
        """
        return {
            TouchRingMode.ONE: "key 4",  # rotate right
            TouchRingMode.TWO: "key +plus",  # zoom in
            TouchRingMode.THREE: "key +altgr 8 key +altgr 8 key +altgr 8",  # increase brush size
            TouchRingMode.FOUR: "key I",  # increase opacity
        }[Config._get_touch_ring_mode()]

    @staticmethod
    def get_abs_wheel_down_mode() -> str:
        """
        Wheel modes when turning/sliding right.
        :return: key sequence (see man xsetwacom)
        """
        return {
            TouchRingMode.ONE: "key 6",  # rotate left
            TouchRingMode.TWO: "key +minus",  # zoom out
            TouchRingMode.THREE: "key +altgr 9 key +altgr 9 key +altgr 9",  # decrease brush size
            TouchRingMode.FOUR: "key O",  # decrease opacity
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
