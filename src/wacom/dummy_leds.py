import os
import pickle
from typing import List

from src.wacom.LedsState import LedsState


def _current_item(temp_file_abs_path: str, temp_file_name: str, item_name: str) -> int:
    file_name = os.path.join(temp_file_abs_path, temp_file_name)

    try:
        print(f"reading last {item_name} from '{file_name}' ...")
        temp_file = open(file_name, "rb")
        last_item = int(pickle.loads(temp_file.read()))
        temp_file.close()
    except (Exception,):
        print(f"failed to load {item_name} from file")
        default_item = 0
        print(f"write {item_name} to file: {default_item}")
        temp_file = open(file_name, "w+b")
        temp_file.truncate()
        temp_file.seek(0)
        pickle.dump(default_item, temp_file)
        temp_file.close()

        print(f"re-reading last {item_name} from '{file_name}' ...")
        temp_file = open(file_name, "rb")
        last_item = int(pickle.loads(temp_file.read()))
        temp_file.close()

    return last_item


def _next_item(temp_file_abs_path: str, temp_file_name: str, max_item: int, item_name: str) -> int:
    """
    Persistently increments/cycles the item-id from 0 to (inclusive) max_item by storing the current value to file.
    :param temp_file_abs_path: path for file
    :param temp_file_name: persistence file (is created if missing)
    :param max_item: max item number
    :param item_name: informative string
    :return: the incremented value
    """
    assert max_item > 0
    file_name = os.path.join(temp_file_abs_path, temp_file_name)

    last_item = _current_item(temp_file_abs_path, temp_file_name, item_name)

    next_item = (1 + last_item) % (max_item + 1)

    temp_file = open(file_name, "w+b")
    temp_file.truncate()
    temp_file.seek(0)
    pickle.dump(next_item, temp_file)
    temp_file.close()

    print(f"last    {item_name} was {last_item}")
    print(f"current {item_name} is  {next_item}")
    return next_item


def read_dummy_leds_brightness(temp_file_abs_path: str, temp_file_name: str, max_item: int, item_name: str, default_on_intensity: int) -> List[int]:
    """
    Fakes the LED brightness by cycling dummy values.

    :param temp_file_abs_path: see `_next_item()`
    :param temp_file_name: see `_next_item()`
    :param max_item: see `_next_item()`
    :param item_name: see `_next_item()`
    :param default_on_intensity: intensity to report for current LED, default off intensity is 0
    :return: dict mapping from LED number (0 == 1st LED) to LED state (intensity, 0 == off)
    """
    print(f"extracting LED status of input device '{item_name}' from:")
    for file in [os.path.join(temp_file_abs_path, temp_file_name)]:
        print(f" - {file}")
    current_led = _current_item(temp_file_abs_path, temp_file_name, item_name=item_name)
    intensities: List[int] = []
    for led_nr in range(0, max_item + 1):
        intensities.append(default_on_intensity if led_nr == current_led else 0)
    print(f" => intensities={intensities}")
    return intensities


def get_active_dummy_led_number(temp_file_abs_path: str, temp_file_name: str, max_item: int = 4, item_name: str = "dummy LED", default_on_intensity: int = 255, default_on_error: int = 99) -> int:
    return LedsState(read_dummy_leds_brightness(temp_file_abs_path, temp_file_name, max_item, item_name, default_on_intensity)).active_led_number(default_on_error)


def toggle_next_dummy_led(temp_file_abs_path: str, temp_file_name: str, max_item: int = 4, item_name: str = "dummy LED") -> int:
    return _next_item(temp_file_abs_path, temp_file_name, max_item, item_name)
