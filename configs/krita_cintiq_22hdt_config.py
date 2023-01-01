import os.path
from typing import Dict

from src.config.BaseConfig import BaseConfig
from src.config.BaseConfig import DeviceParameters
from src.geometry.types import Point, InputArea
from src.wacom.DeviceTypeName import DeviceTypeName


class Config(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.device_hint_expression: str = r"^Wacom Cintiq 22HD(T)? .*"
        self.device_input_area: InputArea = InputArea(Point(0, 0), Point(95440, 53860))
        self.devices_parameters: Dict[DeviceTypeName, DeviceParameters] = {
            DeviceTypeName.PAD:
                DeviceParameters({
                    "Mode": ("Absolute", "absolute mode pointer device"),

                    # ↓ top button, left row
                    "Button 2": ("key +ctrl z", "undo"),
                    "Button 3": ("key shift", "Shift"),
                    "Button 8": ("key ctrl", "Control"),
                    "Button 9": ("key +ctrl +alt 1", "swap with last tool"),

                    "Button 1": ("key 5 2", "reset zoom + rotation"),  # center button

                    "Button 10": ("key 6", "rotate right"),
                    "Button 11": ("key 4", "rotate left"),
                    "Button 12": ("key e", "toggle brush mode: normal/erase"),
                    "Button 13": ("key r", "reset tool"),
                    # ↑ bottom, left row

                    # ↓ top button, right row
                    "Button 15": ("button 15", "-"),
                    "Button 16": ("button 16", "-"),
                    "Button 17": ("button 17", "-"),
                    "Button 18": ("button 18", "reset tool"),

                    "Button 14": ("key tab", "-"),  # center button

                    "Button 19": ("button 19", "-"),
                    "Button 20": ("button 20", "-"),
                    "Button 21": ("button 21", "set all parameters"),
                    "Button 22": ("button 22", "map to next screen"),  # leave default in order to work with xbindkeys without prior configuration by `xsetwacom --config <cfg> configure device --set`
                    # ↑ bottom button, right row

                    # stripes on the backside behind buttons
                    "StripLeftUp": ("key 6", "rotate right"),
                    "StripLeftDown": ("key 4", "rotate left"),
                    "StripRightUp": ("key plus", "zoom in"),
                    "StripRightDown": ("key minus", "zoom out"),
                }),
            DeviceTypeName.STYLUS:
                DeviceParameters({
                    # "PressureCurve": ("70 0 70 100", "stylus pressure curve"),
                    "PressureCurve": ("0 0 100 100", "stylus pressure curve"),
                }),
            DeviceTypeName.ERASER:
                DeviceParameters({
                    # "PressureCurve": ("0 0 50 70", "eraser pressure curve"),
                    "PressureCurve": ("0 0 100 100", "eraser pressure curve"),
                }),
            DeviceTypeName.TOUCH:
                DeviceParameters({
                    "Touch": ("off", "disable touch"),
                }),
        }

        self.xbindkeys_config_string = f"""
# bind button 22 to toggle screens/geometry
"{os.path.join(BaseConfig.root_dir_from_abs_filepath(__file__), 'xsetwacom.py')} --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --map"
b:22

# bind button 21 to trigger a complete re-configuration of the pad
"{os.path.join(BaseConfig.root_dir_from_abs_filepath(__file__), 'xsetwacom.py')} --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --set"
b:21
"""
