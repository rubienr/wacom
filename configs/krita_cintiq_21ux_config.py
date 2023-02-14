import os.path
from typing import Dict

from src.config import models
from src.config.BaseConfig import BaseConfig
from src.config.BaseConfig import DeviceParameters
from src.geometry.types import Point, InputArea
from src.wacom.DeviceTypeName import DeviceTypeName


class Config(BaseConfig):
    def __init__(self) -> None:
        super().__init__(file_path_name=__file__)
        self.device_hint_expression: str = models.WacomCintiq21UX.device_hint
        self.device_input_areas: Dict[DeviceTypeName, InputArea] = {
            DeviceTypeName.STYLUS: InputArea(Point(0, 0), Point(87200, 65600)),
            DeviceTypeName.ERASER: InputArea(Point(0, 0), Point(87200, 65600))
        }
        self.devices_parameters: Dict[DeviceTypeName, DeviceParameters] = {
            DeviceTypeName.PAD:
                DeviceParameters({
                    "Mode": ("Absolute", "absolute mode pointer device"),

                    # ↓ left side, outer row, top button
                    "Button 3": ("key +ctrl z", "undo"),
                    # ↓ left side, inner row, top button
                    "Button 1": ("key shift", "Shift"),
                    "Button 2": ("key ctrl", "Control"),
                    # ↓ left side, bottom
                    "Button 8": ("key 5 2", "reset zoom + rotation"),

                    # ↓ right side, outer row, top button
                    "Button 11": ("button 11", "map to next screen"),
                    # ↓ right side, inner row, top button
                    "Button 9": ("button 9", "-"),
                    "Button 10": ("button 10", "-"),
                    # ↓ right side, bottom
                    "Button 12": ("button 12", "set all parameters"),

                    # touch sensitive stripes
                    "StripLeftUp": ("key plus", "zoom in"),
                    "StripLeftDown": ("key minus", "zoom out"),
                    "StripRightUp": ("key 4", "rotate left"),
                    "StripRightDown": ("key 6", "rotate right"),
                }),
            DeviceTypeName.STYLUS:
                DeviceParameters({
                    "Mode": ("Absolute", "absolute mode pointer device"),
                    "PressureCurve": ("0 0 100 100", "stylus pressure curve"),
                }),
            DeviceTypeName.ERASER:
                DeviceParameters({
                    "Mode": ("Absolute", "absolute mode pointer device"),
                    "PressureCurve": ("0 0 100 100", "eraser pressure curve"),
                })
        }

        self.xbindkeys_config_string = f"""
# bind button 11 to toggle screens/geometry
"{os.path.join(BaseConfig.root_path_from_abs_filepath(__file__), "xsetwacom.py")} --log DEBUG --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --map keep"
b:11

# bind button 12 to trigger a complete re-configuration of the pad
"{os.path.join(BaseConfig.root_path_from_abs_filepath(__file__), "xsetwacom.py")} --log DEBUG --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --set"
b:12
"""
