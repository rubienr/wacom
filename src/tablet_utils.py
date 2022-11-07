import re
import subprocess
from enum import Enum
from typing import Dict, List, Tuple

# ============================================================ section: run command
from configs.base_config import BaseConfig


def _run_subprocess(args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kwargs)


def _lines_from_stream(lines_stream):
    return str(lines_stream.strip()).split('\n') if len(lines_stream) > 0 else []


# ============================================================ section: device wheel / LED status

def get_led_intensities() -> Dict[int, int]:
    lines = _lines_from_stream(_run_subprocess(r"cat /sys/module/wacom/drivers/hid\:wacom/*/input/input*/input*\:\:wacom-0.*/brightness").stdout)
    intensities = dict()
    idx = 0

    for intensity in lines:
        intensities[idx] = int(intensity)
        idx += 1

    return intensities


def get_led_on_off_state() -> Dict[int, bool]:
    intensities = get_led_intensities()
    return {k: intensities[k] > 0 for k in intensities.keys()}


# ============================================================ section: device-ID

class DeviceTypeName(Enum):
    PAD = "PAD"
    STYLUS = "STYLUS"
    ERASER = "ERASER"
    CURSOR = "CURSOR"
    TOUCH = "TOUCH"
    UNKDNOWN = "unknown"


def _run_list_devices() -> List[str]:
    return _lines_from_stream(_run_subprocess("xsetwacom --list devices").stdout)


def _get_device_ids(device_hint_expr: str = ".*") \
        -> List[
            Tuple[
                str,  # device id
                DeviceTypeName,  # device type
                str  # full line
            ]]:
    """
        parse device id from xsetwacom output:

        .. code-block:: bash
           xsetwacom  --list devices
           Wacom Intuos Pro L Finger touch 	id: 15	type: TOUCH
           Wacom Intuos Pro L Pen stylus   	id: 13	type: STYLUS
           Wacom Intuos Pro L Pen eraser   	id: 14	type: ERASER
           Wacom Intuos Pro L Pad pad      	id: 18	type: PAD
        """
    all_devices = [line for line in _run_list_devices()]
    devices = [d for d in all_devices if re.search(device_hint_expr, d) is not None]
    re_matches = [re.match(f".*id:\\s*(\\d*)\\s*type:\\s*(\\w*)\\s*.*", line_with_id) for line_with_id in devices]
    ids = [(match.group(1), match.group(2), match.group(0)) for match in re_matches if match is not None]
    return ids


def get_device_ids(device_hint_expr: str) -> List[str]:
    ids = _get_device_ids(device_hint_expr)
    return [i for i, _name, _info in ids]


def get_stylus_device_ids(device_hint_expr: str) -> List[str]:
    ids = _get_device_ids(device_hint_expr)
    return [i for i, name, _info in ids if name == DeviceTypeName.STYLUS.value]


def get_pad_device_ids(device_hint_expr: str) -> List[str]:
    ids = _get_device_ids(device_hint_expr)
    return [i for i, name, _info in ids if name == DeviceTypeName.PAD.value]


def get_eraser_device_ids(device_hint_expr: str) -> List[str]:
    ids = _get_device_ids(device_hint_expr)
    return [i for i, name, _info in ids if name == DeviceTypeName.ERASER.value]


def get_cursor_device_ids(device_hint_expr: str) -> List[str]:
    ids = _get_device_ids(device_hint_expr)
    return [i for i, name, _info in ids if name == DeviceTypeName.CURSOR.value]


def get_touch_device_ids(device_hint_expr: str) -> List[str]:
    ids = _get_device_ids(device_hint_expr)
    return [i for i, name, _info in ids if name == DeviceTypeName.TOUCH.value]


def print_devices() -> None:
    devices = _get_device_ids()
    if len(devices) > 0:
        print(f"found {len(devices)} device(s):")
        for i, name, info in _get_device_ids():
            info = re.sub("\\s+", " ", info.strip())
            print(f"  - id={i} device={name} ({info})")
    else:
        print("no devices found")


# ============================================================ section: device parameters

def get_all_device_parameters(device_id: str) -> Dict[str, List[str]]:
    lines = _lines_from_stream(_run_subprocess(f"xsetwacom --shell --get {device_id} all").stdout)

    args = dict()
    for line in lines:
        re_match = re.match(f'.*xsetwacom\\s*set\\s"{device_id}"\\s*"([^"]*)"\\s*(.*)', line)
        if re_match:
            arg = re_match.group(1)
            values = re_match.group(2)
            value_list = ['"{}"'.format(v) for v in values.split('"') if v not in ("", " ")]
            args[arg] = value_list

    return args


def print_all_device_parameters(device_id: str) -> None:
    dev_args = get_all_device_parameters(device_id)

    if len(dev_args) > 0:
        print(f"found {len(dev_args)} device parameters for deice_id={device_id}:", end="")
        for k in dev_args.keys():
            print(f"\n  - {k}", end=" ")
            for v in dev_args[k]:
                print(f"{v}", end=" ")
        print()
    else:
        print(f"no device parameters found for deice_id={device_id}")


def print_all_device_parameters_by_device() -> None:
    for device_id, name, _ in _get_device_ids():
        dev_args = get_all_device_parameters(device_id)

        if len(dev_args) > 0:
            print(f"\nfound {len(dev_args)} {name} device parameters for device_id={device_id}:", end="")
            for k in dev_args.keys():
                print(f"\n  - {k}", end=" ")
                for v in dev_args[k]:
                    print(f"{v}", end=" ")
            print()
        else:
            print(f"no device parameters found for deice_id={device_id}")


# ============================================================ section: device parameters

def plot_pressure_curve(points: Tuple[Tuple[int, int], Tuple[int, int]]):
    """
    requires gnuplot
    """
    plot_data = f"0 0\n{points[0][0]} {points[0][1]}\n{points[1][0]} {points[1][1]}\n100 100\n"
    print("bezier pressure curve control points:\nx y")
    print("x y")
    print(f"{plot_data}")
    command = f"echo -e \"{plot_data}e\n\" " \
              f"| tee - a / dev / stdout " \
              f"| gnuplot -p -e \"set grid; " \
              f"plot '-' using 1:2 smooth bezier title 'pressure curve', '' using 1:2 with linespoints pointtype 3 title 'control points'\""
    _run_subprocess(command)


def plot_current_pressure(device_id: str):
    """
    requires xinput and feedgnuplot

    Note: In theory device_id as reported by xsetwacom should match device id from xinput; if not - workaround:

    .. code-block:: bash
       device_info=`xinput --list | grep -i "Pen stylus"`
       declare -a device_ids
       device_ids=(`echo "$device_info" | grep -i "$device_hint" | grep --perl-regexp --only-matching "(?<=id=).*(?=\[)" | tr --delete "[:blank:]"`)
       device_id=${device_ids[0]}
    """
    command = f"xinput --test \"{device_id}\" " \
              r"| awk -F '[[:blank:]]*a\\[[[:digit:]]+\\]=' '{ if ($4 > 0) {print $4 ; fflush()} }' " \
              "| feedgnuplot --exit --stream 0.25 --y2 1 --lines --unset grid --xlen 1000 --ymin 0 --ymax 65536 --y2min 0 --y2max 65536"
    _run_subprocess(command)


# ============================================================ section: configure device

def configure_device(config: BaseConfig):
    assert False


# ============================================================ section: TODO
"""
function set_button_mapping()
function set_device_parameters()
function exit_if_no_device_found()
function print_effective_changes()
function warn_if_device_in_android_mode()
"""
