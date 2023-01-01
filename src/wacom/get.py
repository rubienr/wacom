import os
import re
from typing import List, Optional

from src.utils.decorators import run_once
from src.utils.subprocess import lines_from_stream, run_subprocess
from src.wacom.DeviceInfo import DeviceInfo
from src.wacom.DeviceTypeName import DeviceTypeName
from src.wacom.LedsState import LedsState
from src.wacom.leds import read_leds_brightness


def _run_list_devices() -> List[str]:
    return lines_from_stream(run_subprocess("xsetwacom --list devices").stdout)


def _get_xinput_device_properties(device_id: str) -> List[str]:
    return lines_from_stream(run_subprocess(f"xinput --list-props {device_id}").stdout)


def _filter_device_node_from_xinput_device_properties(properties: List[str]) -> Optional[str]:
    # Example: 'Device Node (280): "/dev/input/event32"'
    for device_property in properties:
        re_match = re.match(r"^.*device\s*node.*[\"']([/\w\d]*)[\"'].*", re.sub(r"\s+", " ", device_property.strip()), re.IGNORECASE)
        if re_match is not None:
            return os.path.basename(os.path.normpath(re_match.group(1)))
    return None


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


def get_active_led_number(device_hint_expr: str, device_type: DeviceTypeName = DeviceTypeName.PAD, default_on_error: int = 99):
    """
    :param device_hint_expr: filter argument for the `xsetwacom list` device listing
    :param device_type: filter argument
    :param default_on_error: default LED number in case of error
    :return: number of first touch-ring LED found to be on, -1 otherwise
    """
    devices_info = get_devices_info(device_hint_expr, [device_type], read_led_intensities=True)
    assert 1 == len(devices_info)
    return devices_info[0].leds_state.active_led_number(default_on_error)


@run_once
def get_active_led_number_once(device_hint_expr: str, device_type: DeviceTypeName = DeviceTypeName.PAD, default_on_error: int = 99):
    return get_active_led_number(device_hint_expr, device_type=device_type, default_on_error=default_on_error)


def get_device_parameter(device_id: str, parameter_name: str) -> str:
    process = run_subprocess(f"xsetwacom --get {device_id.strip()} {parameter_name.strip()}", check=True)
    lines = lines_from_stream(process.stdout)
    assert len(lines) == 1
    return lines[0].strip()


def get_all_device_parameters(device_id: str) -> List[List[str]]:
    lines = lines_from_stream(run_subprocess(f"xsetwacom --shell --get {device_id} all").stdout)

    args: List[List[str]] = []
    for line in lines:
        re_match = re.match(f'.*xsetwacom\\s*set\\s[\'"]{device_id}[\'"]\\s*(.*)', line)
        if re_match:
            values = re_match.group(1)
            arg_and_values_list = [av for av in values.split('"') if av not in ("", " ")]
            args.append(arg_and_values_list)
    return args


def print_devices(devices: Optional[List[DeviceInfo]] = None) -> None:
    devices: List[DeviceInfo] = get_devices_info() if not devices else devices
    if len(devices) > 0:
        print(f"seen {len(devices)} device(s):")
        for dev in devices:
            print(f"  - id={dev.dev_id} name='{dev.name}' type={dev.dev_type.name} input_device='{dev.input_event_logical_name}'")
    else:
        print("no devices found")


def print_all_device_parameters(device_id: str = None) -> None:
    """
    :param device_id: specific device id or None for all devices
    """
    devices_id = [(device_id, "")] if device_id else [(device_id, name) for (device_id, name, _info) in get_devices_info()]
    for device_id, name in devices_id:
        dev_args = [' '.join(args) for args in get_all_device_parameters(device_id)]

        if len(dev_args) > 0:
            print(f"\nfound {len(dev_args)} {name} device parameters for device_id={device_id}:\n", end="")
            for arg_and_value in dev_args:
                print(f"{arg_and_value}")
            print()
        else:
            print(f"no device parameters found for deice_id={device_id}")
