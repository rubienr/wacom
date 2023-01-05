import os
from typing import Dict, Any, Tuple

from src.config.DeviceParameters import DeviceParameters
from src.geometry.types import InputArea, Point
from src.wacom.DeviceTypeName import DeviceTypeName

CONFIG_FILE_MODULE_SUFFIX: str = "_config"
PY_CONFIG_FILE_SUFFIX: str = f"{CONFIG_FILE_MODULE_SUFFIX}.py"


class BaseConfig(object):
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
        self.device_input_area: InputArea = InputArea(Point(), Point())
        self.devices_parameters: Dict[DeviceTypeName, DeviceParameters] = {}
        self.xbindkeys_config_string = ""
        """
        Example:
        
        .. code-block:: bash 
           # bind button 12 to toggle screens
           "./xsetwacom.py --config <config_name> device --map next_fit"
           b:12

           # bind the wheel button to toggle in-between wheel modes
           "./xsetwacom.py --config <config_name> device --set"
           b:10
        """

    def print_config(self, indent_level: int = 0, indent_spaces: int = 2) -> None:
        BaseConfig._print_dict(
            {"device_hint": self.device_hint_expression,
             "devices_input_area": self.device_input_area.to_dict(),
             "devices_parameters": self.devices_parameters,
             "xbindkeys": self.xbindkeys_config_string,
             }, indent_level=indent_level, indent_spaces=indent_spaces)

    @staticmethod
    def _print_dict(container: Dict[str, Any], indent_level: int = 0, indent_spaces: int = 2) -> None:
        indent = " " * indent_level * indent_spaces
        for key, value in container.items():
            if isinstance(value, str) or isinstance(value, int):
                print(f"{indent}{key}: {value}")
            elif isinstance(value, Tuple):
                print(f"{indent}{key}: {value[0]} ({value[1]})")
            elif callable(value):
                evaluated = value()
                print(f"{indent}{key}: {evaluated[0]} ({evaluated[1]})")
            elif isinstance(value, dict):
                print(f"{indent}{key}:")
                BaseConfig._print_dict(container[key], indent_level=indent_level + 1, indent_spaces=indent_spaces)
            elif isinstance(value, DeviceParameters):
                print(f"{indent}{key}:")
                BaseConfig._print_dict(container[key].args, indent_level=indent_level + 1, indent_spaces=indent_spaces)
            else:
                print(f"unexpected config value type: {type(value)}")
                assert False

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
