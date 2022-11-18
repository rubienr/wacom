from typing import Dict

from src.DeviceTypeName import DeviceTypeName
from src.base_config import BaseConfig
from src.base_config import DeviceParameters
from src.geometry_types import Point, InputArea


class Config(BaseConfig):
    def __init__(self):
        super().__init__()
        self.device_hint_expression: str = ".*Wacom Inutos BT.*"
        self.device_input_area: InputArea = InputArea(Point(0, 0), Point(15200, 9500))
        self.devices_parameters: Dict[DeviceTypeName, DeviceParameters] = {
            DeviceTypeName.PAD:
                DeviceParameters({
                    "Mode": ("Absolute", "absolute mode pointer device"),
                    # ↓ top button
                    "Button 1": ("key p", "select paintbrush"),
                    "Button 2": ("key +x -x", "swap colours"),
                    "Button 3": "",  #
                    "Button 8": ("button 8", "set all parameters and map to next screen"),
                }),
            DeviceTypeName.STYLUS: DeviceParameters({
                "PressureCurve": ("70 0 70 100", "stylus pressure curve"),
            }),
            DeviceTypeName.ERASER: DeviceParameters({
                "PressureCurve": ("0 0 50 70", "eraser pressure curve"),
            }),
        }

        self.xbindkeys_config_string = f"""
# bind button 8 to set all parameters and then cycle screens
"./xsetwacom.py --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --set &&\
 ./xsetwacom.py --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --map"
b:8
"""
