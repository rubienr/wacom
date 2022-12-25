import os.path
from enum import Enum
from typing import Dict, Tuple

from src.DeviceTypeName import DeviceTypeName
from src.base_config import BaseConfig
from src.base_config import DeviceParameters
from src.geometry_types import Point, InputArea
from src.tablet_utils import get_active_led_number


class TouchRingMode(Enum):
    ONE = 0  # top left indicator LED
    TWO = 1  # top center indicator LED
    THREE = 2  # top right indicator LED
    UNDEFINED = 99


"""
Notes:
  - if multiple remotes are connected to one dongle then `xsetwacom list` reports multiple "Express Key Remote Pad" devices too
  - to unpair
    ```bash
    find /sys/devices -regex ".*unpair_remote.*"
    /sys/devices/pci0000:00/0000:00:00.1/0000:01:00.1/usb1/5-2/5-2.1/1-2.1:1.0/0001:001:0001.0001/wacom_remote/unpair_remote
    cd /sys/devices/pci0000:00/0000:00:00.1/0000:01:00.1/usb1/5-2/5-2.1/1-2.1:1.0/0001:001:0001.0001/wacom_remote/
    sudo echo "*" > unpair_remote 
    ``` 
"""


class Config(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.device_hint_expression: str = r".*Wacom Express Key Remote Pad pad.*"
        self.device_input_area: InputArea = InputArea(Point(0, 0), Point(95440, 53860))
        self.devices_parameters: Dict[DeviceTypeName, DeviceParameters] = {
            DeviceTypeName.PAD:
                DeviceParameters({
                    # wheel buttons
                    "Button 3": ("button 10", "-"),  # top left
                    "Button 8": ("button 8", "-"),  # top right
                    "Button 9": ("button 9", "-"),  # right
                    "Button 10": ("button 3", "-"),  # bottom
                    "Button 2": ("key +ctrl z", "undo"),  # left
                    # leave default in order to work with xbindkeys without prior configuration by `xsetwacom --config <cfg> configure device --set`
                    "Button 1": ("button 23", "re-configure device"),  # center; default value "button 1" interferes with left mouse button

                    #  ⃔  ⃕ wheel up/down
                    "AbsWheelUp": Config.get_abs_wheel_up_mode,  # call-able retrieving the corresponding mode according to the touch-ring LED state
                    "AbsWheelDown": Config.get_abs_wheel_down_mode,  # call-able retrieving the corresponding mode according to the touch-ring LED state

                    # ↓  top, left outer row
                    "Button 11": ("key shift", "Shift"),
                    "Button 14": ("key ctrl", "Control"),
                    "Button 17": ("button 17", "-"),
                    "Button 21": ("button 21", "-"),
                    # ↑ bottom, left outer row

                    # ↓  top, center row
                    "Button 12": ("key 5 2", "reset zoom + rotation"),
                    "Button 15": ("key r", "reset tool"),
                    "Button 18": ("button 18", "-"),
                    "Button 20": ("button 20", "-"),
                    # ↑ bottom, center row

                    # ↓  top, right outer row
                    "Button 13": ("key e", "toggle brush mode: normal/erase"),
                    "Button 16": ("key +ctrl +alt 1", "swap with last tool"),
                    "Button 19": ("button 19", "-"),
                    "Button 22": ("button 22", "-"),
                    # ↑ bottom, right outer row

                }),
        }

        self.xbindkeys_config_string = f"""
# bind button "23" to trigger a complete re-configuration of the pad depending on the LEDs state
"{os.path.join(BaseConfig.root_dir_from_abs_filepath(__file__), 'xsetwacom.py')} --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --set"
b:23
"""

    @staticmethod
    def get_abs_wheel_up_mode() -> Tuple[str, str]:
        """
        Wheel modes when turning/sliding left.
        :return: key sequence (see man xsetwacom)
        """
        return {
            TouchRingMode.ONE: ("key 4", "rotate left"),
            TouchRingMode.TWO: ("key +minus", "zoom out"),
            TouchRingMode.THREE: ("key +altgr 8 key +altgr 8 key +altgr 8", "decrease brush size"),
            TouchRingMode.UNDEFINED: ("button 5", "fallback"),
        }[TouchRingMode(get_active_led_number(TouchRingMode.UNDEFINED.value))]

    @staticmethod
    def get_abs_wheel_down_mode() -> Tuple[str, str]:
        """
        Wheel modes when turning/sliding right.
        :return: key sequence (see man xsetwacom)
        """
        return {
            TouchRingMode.ONE: ("key 6", "rotate right"),
            TouchRingMode.TWO: ("key +plus", "zoom in"),
            TouchRingMode.THREE: ("key +altgr 9 key +altgr 9 key +altgr 9", "increase brush size"),
            TouchRingMode.UNDEFINED: ("button 4", "fallback"),
        }[TouchRingMode(get_active_led_number(TouchRingMode.UNDEFINED.value))]
