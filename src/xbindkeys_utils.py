import os.path
import subprocess


def _run_subprocess(args: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, shell=True, text=True, **kwargs)


def xbindkeys_start(config: str, temp_dir: str, run_in_background: bool = False) -> None:
    file_name = ".xbindkeys-cfg.tmp"
    file_path_name = os.path.join(temp_dir, file_name)
    with open(file_path_name, "w+b") as xbindkeys_cfg:
        xbindkeys_cfg.write(config.encode())

    print(f"temporary xbindkeys config {xbindkeys_cfg.name}")
    if run_in_background:
        _run_subprocess(f"xbindkeys --file {file_path_name}", check=True)
    else:
        _run_subprocess(f"xbindkeys --file {xbindkeys_cfg.name} --verbose --nodaemon")


def xbindkeys_reload_config_from_disk() -> None:
    _run_subprocess("killall -HUP xbindkeys")


def xbindkeys_killall() -> None:
    _run_subprocess("killall xbindkeys")
