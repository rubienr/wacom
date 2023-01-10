import os
from enum import Enum


class LogLevel(Enum):
    INFO = 0
    DEBUG = 1


class Env:
    def __init__(self):
        self.script_abs_path: str = os.path.join(os.path.dirname(__file__), "../../")

        self.configs_rel_path_name: str = "configs"
        self.configs_abs_path_name: str = os.path.join(self.script_abs_path, self.configs_rel_path_name)

        self.tmp_files_rel_path: str = ".tmp"
        self.tmp_files_abs_path: str = os.path.join(self.script_abs_path, self.tmp_files_rel_path)

        self.verbosity: LogLevel = LogLevel.INFO


instance: Env = Env()
