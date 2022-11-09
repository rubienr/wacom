import difflib
import re
import subprocess
from typing import List

from src.DeviceTypeName import DeviceTypeName
from src.base_config import BaseConfig, DeviceParameters
from src.tablet_utils import get_devices_info, get_device_id


# ============================================================ section: run command

def _run_subprocess(args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, **kwargs)


def _lines_from_stream(lines_stream):
    return str(lines_stream.strip()).split('\n') if len(lines_stream) > 0 else []


# ============================================================ section: read device parameters

def get_device_parameter(device_id: str, parameter_name: str) -> str:
    process = _run_subprocess(f"xsetwacom --get {device_id.strip()} {parameter_name.strip()}", check=True)
    lines = _lines_from_stream(process.stdout)
    assert len(lines) == 1
    return lines[0].strip()


def get_all_device_parameters(device_id: str) -> List[List[str]]:
    lines = _lines_from_stream(_run_subprocess(f"xsetwacom --shell --get {device_id} all").stdout)

    args: List[List[str]] = []
    for line in lines:
        re_match = re.match(f'.*xsetwacom\\s*set\\s[\'"]{device_id}[\'"]\\s*(.*)', line)
        if re_match:
            values = re_match.group(1)
            arg_and_values_list = [av for av in values.split('"') if av not in ("", " ")]
            args.append(arg_and_values_list)
    return args


def print_all_device_parameters(device_id: str = None) -> None:
    """
    :param device_id: specific device id or None for all devices
    """
    devices_id = [(device_id, "")] if device_id else [(device_id, name) for (device_id, name, _info) in get_devices_info()]
    for device_id, name in devices_id:
        dev_args = [' '.join(args) for args in get_all_device_parameters(device_id)]

        if len(dev_args) > 0:
            print(f"\nfound {len(dev_args)} {name} device parameters for device_id={device_id}:", end="")
            for arg_and_value in dev_args:
                print(f"{arg_and_value}")
            print()
        else:
            print(f"no device parameters found for deice_id={device_id}")


def print_diff(old_args: List[List[str]], new_args: List[List[str]]) -> None:
    old = [" ".join(arg_values) for arg_values in old_args]
    new = [" ".join(arg_values) for arg_values in new_args]
    for d in difflib.unified_diff(old, new, n=0):
        print(d)


# ============================================================ section: write device parameters

def set_device_parameter(device_id: str, parameter_name: str, parameter_value: str) -> None:
    _run_subprocess(f"xsetwacom --set {device_id.strip()} {parameter_name.strip()} {parameter_value.strip()}", check=True)


def set_device_parameters(device_id: str, parameters: DeviceParameters) -> None:
    for parameter, value_or_callable in parameters.args.items():
        value = value_or_callable if isinstance(value_or_callable, str) else value_or_callable()
        set_device_parameter(device_id, parameter, value)


def configure_devices(config: BaseConfig, allowed_device_types: List[DeviceTypeName] = None) -> None:
    """
    :param config: complete device configuration
    :param allowed_device_types: List of specific device to pick from the configuration and send to device (i.e. pad, stylus, eraser, touch).
        Leave None or add DeviceTypeName.ANY to list to pick all.
    """
    allowed_device_types = [DeviceTypeName.ANY] if not allowed_device_types else allowed_device_types

    for device_type in [k for k in config.devices_parameters.keys()]:
        if DeviceTypeName.ANY in allowed_device_types or device_type in allowed_device_types:
            dev_id = get_device_id(config.device_hint_expression, device_type)
            print(f"configure device '{device_type.value}' with device_id={dev_id}")
            old_values = get_all_device_parameters(dev_id)
            set_device_parameters(dev_id, config.devices_parameters[device_type])
            new_values = get_all_device_parameters(dev_id)
            print_diff(old_values, new_values)


"""
function set_button_mapping()
"""
