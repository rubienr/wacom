import os
import re
from typing import List, Optional, Callable

from src.config.Env import LogLevel
from src.config.Env import instance as env
from src.geometry.types import InputArea, Point
from src.utils.decorators import run_once
from src.utils.object_dump import object_dump
from src.utils.subprocess import lines_from_stream, run_subprocess
from src.wacom.DeviceInfo import DeviceInfo
from src.wacom.DeviceTypeName import DeviceTypeName
from src.wacom.LedsState import LedsState
from src.wacom.leds import read_leds_brightness


def _run_list_devices() -> List[str]:
    verbose = env.verbosity == LogLevel.DEBUG
    return lines_from_stream(run_subprocess("xsetwacom --list devices", verbose=verbose).stdout)


def _reset_and_get_default_input_area(device_id: str) -> Optional[InputArea]:
    """
    Resets and then reads the default input area from the device.
    :param device_id: the device to reset and read from
    :return: InputArea if the device supports the "Area" and "ResetArea" parameters.
    """
    verbose = env.verbosity == LogLevel.DEBUG
    lines = lines_from_stream(run_subprocess(f"xsetwacom --set {device_id} ResetArea && xsetwacom --get {device_id} Area", verbose=verbose).stdout)

    if len(lines) != 1:
        return None

    re_match = re.match(r"^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$", lines[0])
    if re_match:
        return InputArea(Point(int(re_match.group(1)), int(re_match.group(2))),
                         Point(int(re_match.group(3)), int(re_match.group(4))))
    return None


def _get_xinput_device_properties(device_id: str) -> List[str]:
    verbose = env.verbosity == LogLevel.DEBUG
    return lines_from_stream(run_subprocess(f"xinput --list-props {device_id}", verbose=verbose).stdout)


def _filter_device_node_from_xinput_device_properties(properties: List[str]) -> Optional[str]:
    # Example: 'Device Node (280): "/dev/input/event32"'
    for device_property in properties:
        re_match = re.match(r"^.*device\s*node.*[\"']([/\w\d]*)[\"'].*", re.sub(r"\s+", " ", device_property.strip()), re.IGNORECASE)
        if re_match is not None:
            return os.path.basename(os.path.normpath(re_match.group(1)))
    return None


def get_devices_info(device_hint_expr: str = ".*",
                     device_types: Optional[List[DeviceTypeName]] = None,
                     reset_device_and_read_input_area: bool = False,
                     led_intensity_reader: Optional[Callable[[str], List[int]]] = None) -> List[DeviceInfo]:
    """
    Parses device info from `xsetwacom` and tries to determine the LED brightness (if supported by device).
    parse device info from `xsetwacom` output::

           xsetwacom  --list devices
           Wacom Intuos Pro L Finger touch 	id: 15	type: TOUCH
           Wacom Intuos Pro L Pen stylus   	id: 13	type: STYLUS
           Wacom Intuos Pro L Pen eraser   	id: 14	type: ERASER
           Wacom Intuos Pro L Pad pad      	id: 18	type: PAD

    :param device_hint_expr:
    :param device_types:
    :param reset_device_and_read_input_area: in order to retrieve the default input area, a reset must be performed
    :param led_intensity_reader: optional callable to retrieve the LEDs status, None to skip this step
    :return:
    """
    requested_device_types = [DeviceTypeName.ANY] if not device_types else device_types
    all_xsetwacom_devices = _run_list_devices()
    xsetwacom_devices = [re.sub(r"\s+", " ", device.strip()) for device in all_xsetwacom_devices if re.search(device_hint_expr, device) is not None]

    devices_info: List[DeviceInfo] = []
    for line_with_id in xsetwacom_devices:
        re_match = re.match("(.*)id:\\s*(\\d*)\\s*type:\\s*(\\w*)\\s*.*", line_with_id)
        if re_match is not None:
            dev_name, dev_id, dev_type = re.sub(r"\s+", " ", re_match.group(1).strip()), re_match.group(2), DeviceTypeName(re_match.group(3))
            if dev_type in requested_device_types or DeviceTypeName.ANY in requested_device_types:
                logical_name = _filter_device_node_from_xinput_device_properties(_get_xinput_device_properties(dev_id))
                intensities = led_intensity_reader(logical_name) if led_intensity_reader is not None else []
                devices_info.append(DeviceInfo(
                    dev_id,
                    dev_type,
                    dev_name,
                    logical_name,
                    LedsState(intensities),
                    _reset_and_get_default_input_area(dev_id) if reset_device_and_read_input_area else None))

    return devices_info


def get_device_info(device_hint_expr: str = ".*",
                    device_types: Optional[List[DeviceTypeName]] = None,
                    reset_device_and_read_input_area: bool = False,
                    led_intensity_reader: Optional[Callable[[str], List[int]]] = None) -> DeviceInfo:
    """
    :param device_hint_expr: see `get_devices_info()`
    :param device_types: see `get_devices_info()`
    :param reset_device_and_read_input_area: see `get_devices_info()`
    :param led_intensity_reader: see `get_devices_info()`
    :return: see `get_devices_info()`
    """
    devices_info = get_devices_info(device_hint_expr, device_types, reset_device_and_read_input_area, led_intensity_reader)
    assert 1 == len(devices_info)
    return devices_info[0]


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


def get_active_led_number(device_hint_expr: str,
                          device_type: DeviceTypeName = DeviceTypeName.PAD,
                          default_on_error: int = 99,
                          led_intensity_reader: Callable[[str], List[int]] = read_leds_brightness) -> int:
    """
    :param device_hint_expr: filter argument for the `xsetwacom list` device listing
    :param device_type: filter argument
    :param default_on_error: default LED number in case of error
    :param led_intensity_reader: LED status reader implementation
    :return: number of first touch-ring LED found to be on, default_on_error otherwise
    """
    devices_info = get_devices_info(device_hint_expr, [device_type], led_intensity_reader=led_intensity_reader)
    assert 1 == len(devices_info)
    return devices_info[0].leds_state.active_led_number(default_on_error)


@run_once
def get_active_led_number_once(device_hint_expr: str,
                               device_type: DeviceTypeName = DeviceTypeName.PAD,
                               default_on_error: int = 99,
                               led_intensity_reader: Callable[[str], List[int]] = read_leds_brightness) -> int:
    return get_active_led_number(device_hint_expr, device_type=device_type, default_on_error=default_on_error, led_intensity_reader=led_intensity_reader)


def get_device_parameter(device_id: str, parameter_name: str) -> str:
    verbose = env.verbosity == LogLevel.DEBUG
    process = run_subprocess(f"xsetwacom --get {device_id.strip()} {parameter_name.strip()}", verbose=verbose, check=True)
    lines = lines_from_stream(process.stdout)
    assert len(lines) == 1
    return lines[0].strip()


def get_all_device_parameters(device_id: str) -> List[List[str]]:
    verbose = env.verbosity == LogLevel.DEBUG
    lines = lines_from_stream(run_subprocess(f"xsetwacom --shell --get {device_id} all", verbose=verbose).stdout)

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
    num_devices = len(devices)
    if num_devices > 0:
        print(f"seen {num_devices} device(s):")
        for dev, dev_id in zip(devices, range(1, num_devices + 1)):
            print(f"  - {dev_id}/{num_devices}")
            print(object_dump(dev, prefix='    '))
    else:
        print("no devices found")


def print_all_device_parameters(device_id: str = None) -> None:
    """
    :param device_id: specific device id or None for all devices
    """
    devices_id = [(device_id, "")] if device_id else [(dev_info.dev_id, dev_info.name) for dev_info in get_devices_info()]
    num_devices = len(devices_id)
    print(f"seen {num_devices} devices")
    for (dev_id, name), dev_nr in zip(devices_id, range(1, num_devices + 1)):
        dev_args = [' '.join(args) for args in get_all_device_parameters(dev_id)]
        if len(dev_args) > 0:
            print(f"  - {dev_nr}/{num_devices}: found {len(dev_args)} device parameters for device_id={dev_id} ({name})\n", end="")
            for arg_and_value in dev_args:
                print(f"    {arg_and_value}")
        else:
            print(f"no device parameters found for deice_id={dev_id}")
