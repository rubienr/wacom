from typing import List

from src.utils.subprocess import lines_from_stream, run_subprocess


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

    files = lines_from_stream(run_subprocess(f"ls {file_path}").stdout)
    if 0 < len(files):
        print(f"extracting LED status of input device '{logical_name}' from:")
        for file in files:
            print(f" - {file}")
        intensities = [int(intensity) for intensity in lines_from_stream(run_subprocess(f"cat {file_path}").stdout)]
        print(f" => intensities={intensities}")
        return intensities
    else:
        print(f"no LED status found for '{logical_name}'")
        return []
