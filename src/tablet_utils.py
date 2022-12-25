import re
import subprocess
from typing import Dict, List, Tuple, Optional

from src.DeviceTypeName import DeviceTypeName


# ============================================================ section: run command

def _run_subprocess(args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, **kwargs)


def _lines_from_stream(lines_stream):
    return str(lines_stream.strip()).split('\n') if len(lines_stream) > 0 else []


# ============================================================ section: device wheel / LED status

def get_leds_brightness() -> Dict[int, int]:
    """
    Tested with:
     - Intuos Pro
     - Express Key Remote
    Note: not tested with multiple devices that support LEDs connected at the same time (will not work as expected).
    :return: dict mapping from LED number (0 == 1st LED) to LED state (intensity, 0 == off)
    """
    lines = _lines_from_stream(_run_subprocess(r"cat /sys/module/wacom/drivers/hid\:wacom/*/input/input*/input*\:\:wacom-0.*/brightness").stdout)
    intensities = dict()
    idx = 0

    for intensity in lines:
        intensities[idx] = int(intensity)
        idx += 1

    return intensities


def get_leds_on_off_state() -> Dict[int, bool]:
    """
    :return: dict mapping from LED number to on-off state; True == on (intensity > 0), else False == off
    """
    intensities = get_leds_brightness()
    return {k: intensities[k] > 0 for k in intensities.keys()}


def get_active_led_number(default_on_error: int) -> int:
    """
    :return: number of first touch-ring LED found to be on, -1 otherwise
    """
    states: Dict[int, bool] = get_leds_on_off_state()
    for led_nr, is_on in states.items():
        if is_on:
            return int(led_nr)
    return default_on_error


# ============================================================ section: device-ID

def _run_list_devices() -> List[str]:
    return _lines_from_stream(_run_subprocess("xsetwacom --list devices").stdout)


def get_devices_info(device_hint_expr: str = ".*", device_types: Optional[List[DeviceTypeName]] = None) \
        -> List[
            Tuple[
                str,  # device id
                DeviceTypeName,  # device type
                str  # huma readable string as reported by xsetwacom
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
    device_types = [DeviceTypeName.ANY] if not device_types else device_types
    all_devices = [line for line in _run_list_devices()]
    devices = [device for device in all_devices if re.search(device_hint_expr, device) is not None]
    re_matches = [re.match(f".*id:\\s*(\\d*)\\s*type:\\s*(\\w*)\\s*.*", line_with_id) for line_with_id in devices]
    ids = [(match.group(1), match.group(2), match.group(0)) for match in re_matches if match is not None]
    return [(i, name, info) for (i, name, info) in ids if name in [t.value for t in device_types] or DeviceTypeName.ANY in device_types]


def get_devices_id(device_hint_expr: str, device_type: Optional[DeviceTypeName] = None) -> List[str]:
    return [i for (i, _name, _info) in get_devices_info(device_hint_expr, [device_type] if device_type else None)]


def get_device_id(device_hint_expr: str, device_type: Optional[DeviceTypeName] = None) -> Optional[str]:
    ids = get_devices_id(device_hint_expr, device_type)
    if len(ids) == 0:
        print_devices()
        print(f"no device type='{device_type.name}' matching hint criteria '{device_hint_expr}' found")

    if len(ids) > 1:
        print_devices()
        print(f"device ambiguity for type={device_type.name} with hint criteria '{device_hint_expr}'")
        print_devices(get_devices_info(device_hint_expr))

    return ids[0] if len(ids) > 0 else None


def print_devices(devices: Optional[List[Tuple[str, DeviceTypeName, str]]] = None) -> None:
    devices = get_devices_info() if not devices else devices
    if len(devices) > 0:
        print(f"seen {len(devices)} device(s):")
        for i, name, info in devices:
            info = re.sub("\\s+", " ", info.strip())
            print(f"  - id={i} device={name} ({info})")
    else:
        print("no devices found")


# ============================================================ section: stylus pressure curve

def plot_pressure_curve(two_points: Tuple[Tuple[int, int], Tuple[int, int]]) -> None:
    """
    requires gnuplot
    """
    plot_data = f"0 0\\n{two_points[0][0]} {two_points[0][1]}\\n{two_points[1][0]} {two_points[1][1]}\\n100 100\\n"
    print("bezier pressure curve control points:\nx y")
    print(f"{plot_data}")
    # TODO - pythonic way
    # TODO - fix plot
    command = f"echo -e \"{plot_data}e\\n\" " \
              f"| tee -a /dev/stdout " \
              f"| gnuplot -p -e \"set grid; plot '-' using 1:2 smooth bezier title 'pressure curve', '' using 1:2 with linespoints pointtype 3 title 'control points'\""
    print(command)
    _run_subprocess(command)


def plot_current_pressure(device_id: str) -> None:
    """
    requires xinput and feedgnuplot

    Note: In theory device_id as reported by xsetwacom should match device id from xinput; if not - workaround:

    .. code-block:: bash
       device_info=`xinput --list | grep -i "Pen stylus"`
       declare -a device_ids
       device_ids=(`echo "$device_info" | grep -i "$device_hint" | grep --perl-regexp --only-matching "(?<=id=).*(?=\[)" | tr --delete "[:blank:]"`)
       device_id=${device_ids[0]}
    """
    # TODO - pythonic way
    command = f"xinput --test \"{device_id}\" " \
              r"| awk -F '[[:blank:]]*a\\[[[:digit:]]+\\]=' '{ if ($4 > 0) {print $4 ; fflush()} }' " \
              "| feedgnuplot --exit --stream 0.25 --y2 1 --lines --unset grid --xlen 1000 --ymin 0 --ymax 65536 --y2min 0 --y2max 65536"
    _run_subprocess(command)


# ============================================================ section: TODO

"""
function exit_if_no_device_found()
function warn_if_device_in_android_mode()
"""
