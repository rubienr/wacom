import importlib
import os
from typing import List, Optional

from src.config.BaseConfig import BaseConfig, PY_CONFIG_FILE_SUFFIX, CONFIG_FILE_MODULE_SUFFIX


class ConfigName:
    def __init__(self, base_path: str, file_name: str) -> None:
        self.config_name: str = file_name.removesuffix(PY_CONFIG_FILE_SUFFIX)
        self.base_path: str = base_path
        self.file_name: str = file_name


class ConfigLoader:
    """
    Class to load configuration from file.
    """

    def __init__(self, path_to_config: str, config_name: str) -> None:
        self.path_to_config_folder = path_to_config
        self.package_name = config_name
        self.config_path = os.path.join(self.path_to_config_folder, self.package_name)
        self.config: Optional[BaseConfig] = None

    def config_names(self) -> List[ConfigName]:
        """
        :return: List of seen configurations.
        """
        return [ConfigName(self.path_to_config_folder, file_name) for file_name in ConfigLoader._py_files(self.config_path) if "base_config.py" not in file_name]

    def load_config(self, config_name: str, verbose=False) -> BaseConfig:
        """
        Loads configuration from file.

        :param config_name: configuration name
        :param verbose: True verbosity on (prints loaded configuration); False verbosity off
        :return: the loaded configuration
        """
        if not self.config:
            assert config_name in [f.config_name for f in self.config_names()]
            importlib.invalidate_caches()
            config_name += CONFIG_FILE_MODULE_SUFFIX
            module = importlib.import_module(f".{config_name}", self.package_name)
            self.config = module.Config()
            print(f"config '{config_name}' loaded")
            if verbose:
                self.config.print_config()
        return self.config

    @staticmethod
    def _py_files(config_path: str) -> List[str]:
        return [f for f in os.listdir(config_path) if os.path.isfile(os.path.join(config_path, f)) and f.endswith(PY_CONFIG_FILE_SUFFIX)]
