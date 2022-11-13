import subprocess
import tempfile


def _run_subprocess(args: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, shell=True, text=True, **kwargs)


def xbindkeys_start_foreground(config: str) -> None:
    with tempfile.NamedTemporaryFile(mode='w+b', prefix="xbindkeys-cfg-for-xsetwacom-", suffix=".tmp", delete=True) as xbindkeys_cfg:
        xbindkeys_cfg.write(config.encode())
        xbindkeys_cfg.flush()
        print(f"temporary xbindkeys config {xbindkeys_cfg.name}")
        _run_subprocess(f"xbindkeys --file {xbindkeys_cfg.name} --verbose --nodaemon")


def xbindkeys_start_background(config: str) -> None:
    xbindkeys_cfg = tempfile.NamedTemporaryFile(mode='w+b', prefix="xbindkeys-cfg-for-xsetwacom-", suffix=".tmp", delete=False)
    xbindkeys_cfg.write(config.encode())
    xbindkeys_cfg.flush()
    print(f"temporary xbindkeys config {xbindkeys_cfg.name}")
    _run_subprocess(f"xbindkeys --file {xbindkeys_cfg.name}", check=True)
    # TODO: tmp config file is never removed


def xbindkeys_reload_config_from_disk() -> None:
    _run_subprocess("killall -HUP xbindkeys")


def xbindkeys_killall() -> None:
    _run_subprocess("killall xbindkeys")
