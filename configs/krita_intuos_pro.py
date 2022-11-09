from typing import Dict

from src.base_config import BaseConfig
from src.DeviceTypeName import DeviceTypeName
from src.base_config import DeviceParameters


class Config(BaseConfig):
    def __init__(self):
        super().__init__()
        self.device_hint_expression: str = ".*Wacom Intuos Pro.*"
        self.devices_parameters: Dict[DeviceTypeName: DeviceParameters] = {
            DeviceTypeName.PAD:
                DeviceParameters({
                    # ↓ top button
                    "Button 1": "key +ctrl z",  # undo
                    "Button 2": "key shift",  # Shift
                    "Button 3": "key ctrl",  # Control
                    "Button 8": "key +ctrl +alt 1",  # swap with last tool
                    # ↑ 4th button
                    # ↓ touch ring button
                    "Button 13": "button 10",  # toggle modes
                    # ↓ 5th button
                    "Button 9": "key e",  # toggle brush mode: normal/erase
                    "Button 10": "key 5 2",  # reset zoom + rotation
                    "Button 11": "key r",  # reset tool
                    "Button 12": "button 12",  # map to next screen
                    # ↑ bottom button
                }),
        }

        self.wheel_modes = {
            "up": {
                # top left ring indicator led = 1
                1: "key 4",  # rotate
                2: "key +plus",  # zoom
                3: "key +altgr 8 key +altgr 8 key +altgr 8",  # increase brush size
                0: "key I",  # increase opacity
                # bottom left ring indicator led = 0
            },
            "down": {
                # top left ring indicator led = 1
                1: "key 6",  # rotate
                2: "key +minus",  # zoom
                3: "key +altgr 9 key +altgr 9 key +altgr 9",  # decrease brush size
                0: "key O",  # decrease opacity
                # bottom left ring indicator led = 0
            }
        }

        self.xbindkeys_config_string = """ 
# bind button 12 to toggle screens
"./xsetwacom.py --config krita-intuos-pro --map next"
b:12

# bind wheel button to toggle the wheel mode
"./xsetwacom.py --config krita-intuos-pro"
b:10
"""

        self.pressure_curve = {
            DeviceTypeName.ERASER: ((0, 0), (50, 70)),
            DeviceTypeName.STYLUS: ((70, 0), (70, 100)),
        }
