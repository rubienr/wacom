import os
from typing import Dict

from src.config.DeviceParameters import DeviceParameters
from src.config.Mode import Mode
from src.geometry.types import InputArea
from src.utils.object_dump import object_dump
from src.wacom.DeviceTypeName import DeviceTypeName

CONFIG_FILE_MODULE_SUFFIX: str = "_config"
PY_CONFIG_FILE_SUFFIX: str = f"{CONFIG_FILE_MODULE_SUFFIX}.py"


class BaseConfig:
    """
    Base class each configuration profile must derive from.
    """

    def __init__(self, file_path_name: str = __file__) -> None:
        self.device_hint_expression: str = ""
        """
        - i.e. regex r"^Wacom Intuos Pro .*",
        - shall match the device as accurate as possible
        - see `xsetwacom --list devices`
        """
        self.file_path_name: str = file_path_name
        self.device_input_areas: Dict[DeviceTypeName, InputArea] = {}
        """
        Typical devices with input area are stylus, eraser and touch.
        Stylus and eraser mostly share same resolution where the touch input usually has lower resolution.

        See::
            xsetwacom list devices
            xsetwacom --set <id> ResetArea
            xsetwacom --get <id> Area
        """
        self.devices_parameters: Dict[DeviceTypeName, DeviceParameters] = {}
        self.modes: Dict[str, Mode] = {}
        """
        additional LED independent modes can be defined here, i.e.
        - devices without touch ring LEDs have no modes: this can simulate multiple modes
        - devices with touch: toggle touch on/off
        """
        self.xbindkeys_config_string = ""
        """
        Example::

           # bind button 12 to toggle screens
           "./xsetwacom.py --config <config_name> device --map keep"
           b:12

           # bind the wheel button to toggle in-between wheel modes
           "./xsetwacom.py --config <config_name> device --set"
           b:10
        """

    def print_config(self, prefix: str = "", indent: str = "  ", level: int = 0) -> None:
        print(object_dump(self, prefix, indent, level))

    @staticmethod
    def config_name_from_abs_filepath(file_path_with_py_extension: str) -> str:
        """
        Returns the config name from file path.
        :param file_path_with_py_extension: path as reported by `__file__`
        :return: the configuration name
        """
        return os.path.basename(file_path_with_py_extension).removesuffix(PY_CONFIG_FILE_SUFFIX)

    @staticmethod
    def root_path_from_abs_filepath(config_file: str) -> str:
        """
        Returns the script root directory of xsetwacom.py.
        :param config_file: __file__
        :return: the root directory as seen from the configuration file
        """
        return os.path.join(os.path.dirname(config_file), "../")

    @property
    def file_path(self) -> str:
        """
        :return: absolute path to configuration file
        """
        return os.path.dirname(self.file_path_name)

    @property
    def file_name(self) -> str:
        """
        :return: the configuration file name inclusive suffix; i.e. xxx_yyy_zzz_config.py
        """
        return os.path.basename(self.file_path_name)

    @property
    def name(self) -> str:
        """
        :return: the configuration file name without suffix; i.e. xxx_yyy_zzz if the configuration file is xxx_yyy_zzz_config.py
        """
        return BaseConfig.config_name_from_abs_filepath(self.file_path_name)
