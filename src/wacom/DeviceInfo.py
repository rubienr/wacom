from typing import Optional

from src.wacom.DeviceTypeName import DeviceTypeName
from src.wacom.LedsState import LedsState


class DeviceInfo(object):
    def __init__(self, dev_id: str, dev_type: DeviceTypeName, name: str, input_event_logical_name: Optional[str], leds_state: LedsState) -> None:
        self.dev_id: str = dev_id  # from xsetwacom, assume it coincides with xinput id
        self.dev_type: DeviceTypeName = dev_type  # from xsetwacom
        self.name: str = name  # from xsetwacom
        self.input_event_logical_name: str = input_event_logical_name  # from `xinput X | grep "Device Node"`
        self.leds_state: LedsState = leds_state  # from /sys/class/input/...
