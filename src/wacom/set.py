import difflib
from typing import List, Tuple

from src.config.BaseConfig import BaseConfig, DeviceParameters
from src.utils.subprocess import run_subprocess
from src.wacom.DeviceTypeName import DeviceTypeName
from src.wacom.get import get_device_id, get_all_device_parameters, print_devices


def print_diff(old_args: List[List[str]], new_args: List[List[str]]) -> None:
    old = [" ".join(arg_values) for arg_values in old_args]
    new = [" ".join(arg_values) for arg_values in new_args]
    for d in difflib.unified_diff(old, new, n=0):
        print(d)


def set_device_parameter(device_id: str, parameter_name: str, parameter_value: str) -> None:
    run_subprocess(f"xsetwacom --set {device_id.strip()} {parameter_name.strip()} {parameter_value.strip()}", check=True)


def set_device_parameters(device_id: str, parameters: DeviceParameters) -> None:
    for parameter, value_or_callable in parameters.args.items():
        value, _help_text = value_or_callable if isinstance(value_or_callable, Tuple) else value_or_callable()
        set_device_parameter(device_id, parameter, value)


def configure_devices(config: BaseConfig, allowed_device_types: List[DeviceTypeName] = None) -> None:
    """
    :param config: complete device configuration
    :param allowed_device_types: List of specific device to pick from the configuration and send to device (i.e. pad, stylus, eraser, touch).
        Leave None or add DeviceTypeName.ANY to list to pick all.
    """
    allowed_device_types = [DeviceTypeName.ANY] if not allowed_device_types else allowed_device_types

    print_devices()
    print(f"configuring device hint='{config.device_hint_expression}', types={[d.name for d in allowed_device_types]}")

    for device_type in [k for k in config.devices_parameters.keys()]:
        if DeviceTypeName.ANY in allowed_device_types or device_type in allowed_device_types:
            dev_id = get_device_id(config.device_hint_expression, device_type)
            if dev_id is None:
                print(f"  - WARING: skipping requested configuration of device type={device_type.value} with hint {config.device_hint_expression}")
                continue
            print(f"  - configure device type='{device_type.value}' with device_id={dev_id}")
            old_values = get_all_device_parameters(dev_id)
            set_device_parameters(dev_id, config.devices_parameters[device_type])
            new_values = get_all_device_parameters(dev_id)
            print("  - touched parameters (diff):")
            print(">>>>")
            print_diff(old_values, new_values)
            print("<<<<")
