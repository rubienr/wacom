from typing import Optional

from src.geometry.types import InputArea
from src.wacom.DeviceTypeName import DeviceTypeName
from src.wacom.LedsState import LedsState


class DeviceInfo:
    def __init__(self, dev_id: str, dev_type: DeviceTypeName, name: str, input_event_logical_name: Optional[str], leds_state: LedsState, input_area: Optional[InputArea]) -> None:
        self.dev_id: str = dev_id  # from xsetwacom, assume the id coincides with the xinput id
        self.dev_type: DeviceTypeName = dev_type  # from xsetwacom
        self.name: str = name  # from xsetwacom
        self.input_area: Optional[InputArea] = input_area  # from xsetwacom

        self.input_event_logical_name: str = input_event_logical_name  # from `xinput X | grep "Device Node"`
        self.leds_state: LedsState = leds_state  # from /sys/class/input/...
