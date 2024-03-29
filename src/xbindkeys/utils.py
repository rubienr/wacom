import os.path
import subprocess

from src.config.Env import LogLevel
from src.config.Env import instance as env
from src.utils.subprocess import run_subprocess


def _run_subprocess(args: str, **kwargs) -> subprocess.CompletedProcess:
    verbose = env.verbosity == LogLevel.DEBUG
    return run_subprocess(args, stdout=None, stderr=None, shell=True, text=True, verbose=verbose, **kwargs)


def xbindkeys_start(config: str, temp_path: str, config_file_name: str, config_file_suffix: str = ".xbindkeys-cfg", run_in_background: bool = False) -> None:
    """
    Start `xbindkeys` with given configuration and run in foreground or background.

    :param config: configuration for `xbindkeys`
    :param temp_path: directory where to temporarily store the configuration file for `xbindkeys`
    :param config_file_name: temporary config file name
    :param config_file_suffix: suffix for config file
    :param run_in_background: False: run in foreground; True: run in background
    """
    file_path_name = os.path.join(temp_path, config_file_name + config_file_suffix)
    with open(file_path_name, "w+b") as xbindkeys_cfg:
        xbindkeys_cfg.write(config.encode())

    print(f"temporary xbindkeys config {xbindkeys_cfg.name}")
    if run_in_background:
        _run_subprocess(f"xbindkeys --file {file_path_name}", check=True)
    else:
        _run_subprocess(f"xbindkeys --file {xbindkeys_cfg.name} --verbose --nodaemon")


def xbindkeys_reload_config_from_disk() -> None:
    """
    Tell all `xbindkeys` (user) instances to re-load their configurations.
    """

    _run_subprocess("killall -HUP xbindkeys")


def xbindkeys_killall() -> None:
    """
    Kill all (user) `xbindkeys` instances.
    """
    _run_subprocess("killall xbindkeys")
