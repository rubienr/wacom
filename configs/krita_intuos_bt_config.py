import os
from typing import Dict

from src.config.BaseConfig import BaseConfig
from src.config.BaseConfig import DeviceParameters
from src.geometry.types import Point, InputArea
from src.wacom.DeviceTypeName import DeviceTypeName


class Config(BaseConfig):
    def __init__(self) -> None:
        super().__init__(file_path_name=__file__)
        self.device_hint_expression: str = r"^Wacom Inutos BT .*"
        self.device_input_areas: Dict[DeviceTypeName, InputArea] = {DeviceTypeName.STYLUS: InputArea(Point(0, 0), Point(15200, 9500))}
        self.devices_parameters: Dict[DeviceTypeName, DeviceParameters] = {
            DeviceTypeName.PAD:
                DeviceParameters({
                    "Mode": ("Absolute", "absolute mode pointer device"),

                    # ↓ top button
                    "Button 1": ("key +ctrl +alt 1 -ctrl -alt", "script: 10 brushes"),
                    "Button 2": ("key b", "brush tool"),
                    "Button 3": ("key r", "reset tool"),
                    "Button 8": ("button 8", "set all parameters and map to next screen"),
                }),
            DeviceTypeName.STYLUS: DeviceParameters({
                "Mode": ("Absolute", "absolute mode pointer device"),
                "PressureCurve": ("70 0 70 100", "stylus pressure curve"),
            }),
            DeviceTypeName.ERASER: DeviceParameters({
                "Mode": ("Absolute", "absolute mode pointer device"),
                "PressureCurve": ("0 0 50 70", "eraser pressure curve"),
            }),
        }

        self.xbindkeys_config_string = f"""
# bind button 8 to set all parameters and then cycle screens
"{os.path.join(BaseConfig.root_path_from_abs_filepath(__file__), "xsetwacom.py")} --log DEBUG --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --set &&\
 {os.path.join(BaseConfig.root_path_from_abs_filepath(__file__), "xsetwacom.py")} --log DEBUG --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --map keep"
b:8
"""
