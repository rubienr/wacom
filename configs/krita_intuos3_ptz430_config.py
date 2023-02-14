import os
from typing import Dict

from src.config import models
from src.config.BaseConfig import BaseConfig
from src.config.BaseConfig import DeviceParameters
from src.geometry.types import Point, InputArea
from src.wacom.DeviceTypeName import DeviceTypeName


class Config(BaseConfig):
    def __init__(self) -> None:
        super().__init__(file_path_name=__file__)
        self.device_hint_expression: str = models.WacomIntuos3Ptz430.device_hint
        self.device_input_areas: Dict[DeviceTypeName, InputArea] = {
            DeviceTypeName.STYLUS: InputArea(Point(0, 0), Point(25400, 20320)),
            DeviceTypeName.ERASER: InputArea(Point(0, 0), Point(25400, 20320)),
            DeviceTypeName.CURSOR: InputArea(Point(0, 0), Point(25400, 20320))
        }
        self.devices_parameters: Dict[DeviceTypeName, DeviceParameters] = {
            DeviceTypeName.PAD:
                DeviceParameters({
                    "Mode": ("Absolute", "absolute mode pointer device"),

                    # ↓ left row, top button
                    "Button 3": ("key +ctrl z", "undo"),

                    # ↓ right row, top button
                    "Button 1": ("key shift", "Shift"),
                    "Button 2": ("key ctrl", "Control"),
                    # ↑ right row, bottom button

                    # ↓ bottom button
                    "Button 8": ("button 8", "set all parameters and map to next screen"),

                    # touch sensitive stripe
                    "StripLeftUp": ("key plus", "zoom in"),
                    "StripLeftDown": ("key minus", "zoom out")
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
