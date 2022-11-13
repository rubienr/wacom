import importlib
import os
from typing import List, Optional

from src.base_config import BaseConfig, PY_CONFIG_FILE_SUFFIX, CONFIG_FILE_MODULE_SUFFIX


class ConfigName(object):
    def __init__(self, base_path: str, file_name: str):
        self.config_name = file_name.removesuffix(PY_CONFIG_FILE_SUFFIX)
        self.base_path = base_path
        self.file_name = file_name


class ConfigLoader(object):

    def __init__(self, path_to_config_folder: str, config_folder_name: str):
        self.path_to_config_folder = path_to_config_folder
        self.package_name = config_folder_name
        self.config_path = os.path.join(self.path_to_config_folder, self.package_name)
        self.config: Optional[BaseConfig] = None

    def config_names(self) -> List[ConfigName]:
        return [ConfigName(self.path_to_config_folder, file_name) for file_name in ConfigLoader._py_files(self.config_path) if "base_config.py" not in file_name]

    def load_config(self, config_name: str, verbose=False) -> BaseConfig:
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
