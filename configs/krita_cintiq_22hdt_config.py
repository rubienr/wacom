import os.path
from enum import Enum
from typing import Dict, Tuple, Union, Type

from src.config import models
from src.config.BaseConfig import BaseConfig
from src.config.BaseConfig import DeviceParameters
from src.config.Env import instance as env
from src.config.Mode import Mode
from src.geometry.types import Point, InputArea
from src.wacom.DeviceTypeName import DeviceTypeName
from src.wacom.dummy_leds import get_active_dummy_led_number, toggle_next_dummy_led


class DummyTouchRingMode(Enum):
    ONE = 0
    TWO = 1
    UNDEFINED = 99


class TouchMode(Enum):
    ON = 0
    OFF = 1
    UNDEFINED = 99


class Config(BaseConfig):
    def __init__(self) -> None:
        super().__init__(file_path_name=__file__)
        self.device_hint_expression: str = models.WacomCintiq22HDT.device_hint
        self.device_input_areas: Dict[DeviceTypeName, InputArea] = {
            DeviceTypeName.STYLUS: InputArea(Point(0, 0), Point(95440, 53860)),
            DeviceTypeName.ERASER: InputArea(Point(0, 0), Point(95440, 53860)),
            DeviceTypeName.TOUCH: InputArea(Point(0, 0), Point(4752, 2673))
        }
        self.devices_parameters: Dict[DeviceTypeName, DeviceParameters] = {
            DeviceTypeName.PAD:
                DeviceParameters({
                    "Mode": ("Absolute", "absolute mode pointer device"),

                    # ↓ left row, top button
                    "Button 2": ("key +ctrl z", "undo"),
                    "Button 3": ("key shift", "Shift"),
                    "Button 8": ("key ctrl", "Control"),
                    "Button 9": ("key +ctrl +alt 1", "swap with last tool"),

                    "Button 1": ("key 5 2", "reset zoom + rotation"),  # center button

                    "Button 10": ("key 6", "rotate right"),
                    "Button 11": ("key 4", "rotate left"),
                    "Button 12": ("key e", "toggle brush mode: normal/erase"),
                    "Button 13": ("key r", "reset tool"),
                    # ↑ left row, bottom

                    # ↓ right row, top button
                    "Button 15": ("button 15", "-"),
                    "Button 16": ("button 16", "-"),
                    "Button 17": ("button 17", "-"),
                    "Button 18": ("button 18", "-"),

                    "Button 14": ("button 14", "trigger mode switch"),  # center button: trigger mode switch (dummy LED) by xbindkeys

                    "Button 19": ("button 19", "-"),
                    "Button 20": ("button 20", "-"),
                    "Button 21": ("button 21", "set all parameters"),
                    "Button 22": ("button 22", "map to next screen"),  # leave default in order to work with xbindkeys without prior configuration by `xsetwacom --config <cfg> configure device --set`
                    # ↑ right row, bottom button

                    # touch sensitive stripes on the backside behind buttons
                    "StripLeftUp": ("key 6", "rotate right"),
                    "StripLeftDown": ("key 4", "rotate left"),
                    "StripRightUp": ("key plus", "zoom in"),
                    "StripRightDown": ("key minus", "zoom out"),
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
                }),
            DeviceTypeName.TOUCH:
                DeviceParameters({
                    "Mode": ("Absolute", "absolute mode pointer device"),
                    "Touch": ConfigHelper.get_touch_mode,
                }),
        }

        self.modes = {m.name: m for m in [
            Mode("Touch",
                 lambda: ConfigHelper.get_active_mode(TouchMode),
                 lambda: ConfigHelper.toggle_next_mode(TouchMode))
        ]}

        self.xbindkeys_config_string = f"""
# bind button 22 to toggle screens/geometry
"{os.path.join(BaseConfig.root_path_from_abs_filepath(__file__), "xsetwacom.py")} --log DEBUG --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --map keep"
b:22

# bind button 21 to trigger a complete re-configuration of the pad
"{os.path.join(BaseConfig.root_path_from_abs_filepath(__file__), "xsetwacom.py")} --log DEBUG --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --set"
b:21

# mode switch
"{os.path.join(BaseConfig.root_path_from_abs_filepath(__file__), "xsetwacom.py")} --log DEBUG --config {BaseConfig.config_name_from_abs_filepath(__file__)} mode --toggle Touch &&\
 {os.path.join(BaseConfig.root_path_from_abs_filepath(__file__), "xsetwacom.py")} --log DEBUG --config {BaseConfig.config_name_from_abs_filepath(__file__)} device --set"
b:14
"""


class ConfigHelper:

    @staticmethod
    def get_active_mode(mode_enum: Union[Type[DummyTouchRingMode], Type[TouchMode]]) -> Union[DummyTouchRingMode, TouchMode]:
        """
        Retrieves the current persisted mode.

        The persistence file depends on
          - the configuration file name and
          - the requested Enum mode type.

        :param mode_enum: the enum type for witch the current mode shall be retrieved
        :return: the current mode
        """
        path = env.tmp_files_abs_path
        config_name = BaseConfig.config_name_from_abs_filepath(__file__)
        return mode_enum(
            get_active_dummy_led_number(path, f"{config_name}-{mode_enum.__name__}.mode", max_item=len(mode_enum) - 2, default_on_error=int(mode_enum.UNDEFINED.value), item_name=mode_enum.__name__))

    @staticmethod
    def toggle_next_mode(mode_enum: Union[Type[DummyTouchRingMode], Type[TouchMode]]) -> None:
        """
        Cycles persistently to the next mode.

        The persistence file depends on
          - the configuration file name and
          - the requested Enum mode type.

        :param mode_enum: the enum type for which the next mode shall be cycled to
        """
        path = env.tmp_files_abs_path
        config_name = BaseConfig.config_name_from_abs_filepath(__file__)
        toggle_next_dummy_led(path, f"{config_name}-{mode_enum.__name__}.mode", max_item=len(mode_enum) - 2)

    @staticmethod
    def get_touch_mode() -> Tuple[str, str]:
        """
        Wheel modes when turning wheel right.
        :return: key sequence (see man xsetwacom)
        """
        return {
            TouchMode.ON: ("on", "enable touch"),
            TouchMode.OFF: ("off", "disable touch"),
            TouchMode.UNDEFINED: ("off", "fallback"),
        }[ConfigHelper.get_active_mode(TouchMode)]
