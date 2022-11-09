import subprocess
import tempfile
from enum import Enum


class XBindKeysRunMode(Enum):
    START_FOREGROUND = "fg"
    START_BACKGROUND = "bg"
    KILL = "ki"
    RELOAD = "re"


def _run_subprocess(args: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, shell=True, text=True, **kwargs)


def run_xbindkeys(config: str, run_mode: str):
    print(f"invoke xbindkeys (mode={run_mode})")
    if run_mode == XBindKeysRunMode.START_BACKGROUND.value:
        xbindkeys_cfg = tempfile.NamedTemporaryFile(mode='w+b', prefix="xbindkeys-cfg-for-xsetwacom-", suffix=".tmp", delete=False)
        xbindkeys_cfg.write(config.encode())
        xbindkeys_cfg.flush()
        print(f"temporary xbindkeys config {xbindkeys_cfg.name}")
        _run_subprocess(f"xbindkeys --file {xbindkeys_cfg.name}", check=True)
        # TODO: tmp config file is never removed
    elif run_mode == XBindKeysRunMode.START_FOREGROUND.value:
        with tempfile.NamedTemporaryFile(mode='w+b', prefix="xbindkeys-cfg-for-xsetwacom-", suffix=".tmp", delete=True) as xbindkeys_cfg:
            xbindkeys_cfg.write(config.encode())
            xbindkeys_cfg.flush()
            print(f"temporary xbindkeys config {xbindkeys_cfg.name}")
            _run_subprocess(f"xbindkeys --file {xbindkeys_cfg.name} --verbose --nodaemon")
    elif run_mode == XBindKeysRunMode.KILL.value:
        _run_subprocess("killall xbindkeys")
    elif run_mode == XBindKeysRunMode.RELOAD.value:
        _run_subprocess("killall -HUP xbindkeys")
    else:
        print(f"unknown run_mode={run_mode}")
        return False

    return True
