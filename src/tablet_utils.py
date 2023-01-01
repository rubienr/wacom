import os
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

def read_leds_brightness(logical_name: str) -> List[int]:
    """
    Reads the current LED brightness of the specified device from the driver.

    The LED brightness for event EE can be found in
        - /sys/module/wacom/drivers/*/*/input/inputII/*/brightness or better
        -  /sys/class/input/eventEE/device/*/brightness

    To retrieve the logical name (i.e. "event42") the following can be used:
        - `lshw` - good Json API; very slow takes ~0.5sec
        - `lsusb` - weak CLI API; needs vendor/product id
        - `evtest` - needs root permission
        - `xinput` - weak CLI API but fast (recommended)

    :param logical_name: i.e. "event42", see: `xinput --list-props N  | grep "Device Node"
    :return: dict mapping from LED number (0 == 1st LED) to LED state (intensity, 0 == off)
    """
    if logical_name is None:
        print("cannot retrieve LED intensities for device 'None'")
        return []

    file_path = f"/sys/class/input/{logical_name}/device/*/brightness"

    files = _lines_from_stream(_run_subprocess(f"ls {file_path}").stdout)
    if 0 < len(files):
        print(f"extracting LED status of input device '{logical_name}' from:")
        for file in files:
            print(f" - {file}")
        intensities = [int(intensity) for intensity in _lines_from_stream(_run_subprocess(f"cat {file_path}").stdout)]
        print(f" => intensities={intensities}")
        return intensities
    else:
        print(f"no LED status found for '{logical_name}'")
        return []


# ============================================================ section: device info

def _run_list_devices() -> List[str]:
    return _lines_from_stream(_run_subprocess("xsetwacom --list devices").stdout)


def _get_xinput_device_properties(device_id: str) -> List[str]:
    return _lines_from_stream(_run_subprocess(f"xinput --list-props {device_id}").stdout)


def _filter_device_node_from_xinput_device_properties(properties: List[str]) -> Optional[str]:
    # Example: 'Device Node (280): "/dev/input/event32"'
    for device_property in properties:
        re_match = re.match(r"^.*device\s*node.*[\"']([/\w\d]*)[\"'].*", re.sub(r"\s+", " ", device_property.strip()), re.IGNORECASE)
        if re_match is not None:
            return os.path.basename(os.path.normpath(re_match.group(1)))
    return None


class LedsState(object):

    def __init__(self, intensities: List[int]):
        self.intensities: List[int] = intensities

    def on_off_states(self) -> Dict[int, bool]:
        """
        :return: Dict mapping from LED number to on-off state; True == on (intensity > 0), else False == off
        """
        return {idx: self.intensities[idx] > 0 for idx in range(0, len(self.intensities))}

    def active_led_number(self, default_on_error: int = 99) -> int:
        """
        :return: number of first touch-ring LED found to be on, -1 otherwise
        """
        for led_nr, is_on in self.on_off_states().items():
            if is_on:
                return led_nr
        return default_on_error


class DeviceInfo(object):
    def __init__(self, dev_id: str, dev_type: DeviceTypeName, name: str, input_event_logical_name: Optional[str], leds_state: LedsState):
        self.dev_id: str = dev_id  # from xsetwacom, assume it coincides with xinput id
        self.dev_type: DeviceTypeName = dev_type  # from xsetwacom
        self.name: str = name  # from xsetwacom
        self.input_event_logical_name: str = input_event_logical_name  # from `xinput X | grep "Device Node"`
        self.leds_state: LedsState = leds_state  # from /sys/class/input/...


def get_devices_info(device_hint_expr: str = ".*", device_types: Optional[List[DeviceTypeName]] = None, read_led_intensities: bool = False) -> List[DeviceInfo]:
    """
    Parses device info from `xsetwacom` and tries to determine the LED brightness (if supported by device).
        parse device info from `xsetwacom` output:

        .. code-block:: bash
           xsetwacom  --list devices
           Wacom Intuos Pro L Finger touch 	id: 15	type: TOUCH
           Wacom Intuos Pro L Pen stylus   	id: 13	type: STYLUS
           Wacom Intuos Pro L Pen eraser   	id: 14	type: ERASER
           Wacom Intuos Pro L Pad pad      	id: 18	type: PAD
        """
    requested_device_types = [DeviceTypeName.ANY] if not device_types else device_types
    all_xsetwacom_devices = [line for line in _run_list_devices()]
    xsetwacom_devices = [re.sub(r"\s+", " ", device.strip()) for device in all_xsetwacom_devices if re.search(device_hint_expr, device) is not None]

    devices_info: List[DeviceInfo] = []
    for line_with_id in xsetwacom_devices:
        re_match = re.match(f"(.*)id:\\s*(\\d*)\\s*type:\\s*(\\w*)\\s*.*", line_with_id)
        if re_match is not None:
            dev_name, dev_id, dev_type = re.sub(r"\s+", " ", re_match.group(1).strip()), re_match.group(2), DeviceTypeName(re_match.group(3))
            if dev_type in requested_device_types or DeviceTypeName.ANY in requested_device_types:
                logical_name = _filter_device_node_from_xinput_device_properties(_get_xinput_device_properties(dev_id))
                if read_led_intensities:
                    intensities = read_leds_brightness(logical_name)
                else:
                    intensities = []
                devices_info.append(DeviceInfo(
                    dev_id,
                    dev_type,
                    dev_name,
                    logical_name,
                    LedsState(intensities)))

    return devices_info


def get_devices_id(device_hint_expr: str, device_type: Optional[DeviceTypeName] = None) -> List[str]:
    devices_info = get_devices_info(device_hint_expr, [device_type])
    ids = [d.dev_id for d in devices_info]
    if len(ids) == 0:
        print_devices(devices_info)
        print(f"no device type='{device_type.name}' matching hint criteria '{device_hint_expr}' found")
    return ids


def get_device_id(device_hint_expr: str, device_type: Optional[DeviceTypeName] = None) -> Optional[str]:
    devices_info = get_devices_info(device_hint_expr, [device_type])
    ids = [d.dev_id for d in devices_info]
    if len(ids) == 0:
        print_devices(devices_info)
        print(f"no device type='{device_type.name}' matching hint criteria '{device_hint_expr}' found")

    if len(ids) > 1:
        print_devices(devices_info)
        print(f"device ambiguity for type={device_type.name} with hint criteria '{device_hint_expr}'")
        print_devices(devices_info)

    return ids[0] if len(ids) > 0 else None


def print_devices(devices: Optional[List[DeviceInfo]] = None) -> None:
    devices: List[DeviceInfo] = get_devices_info() if not devices else devices
    if len(devices) > 0:
        print(f"seen {len(devices)} device(s):")
        for dev in devices:
            print(f"  - id={dev.dev_id} name='{dev.name}' type={dev.dev_type.name} input_device='{dev.input_event_logical_name}'")
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
