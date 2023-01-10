from typing import Tuple, Optional

import pytest

import src.wacom.get as wacom
from src.wacom.DeviceTypeName import DeviceTypeName


class TestParseDeviceFromListing:

    @pytest.mark.parametrize("item, expected_result",
                             [
                                 ("Wacom Cintiq 22HDT Pad pad              id: 8   type: PAD", ("Wacom Cintiq 22HDT Pad pad", "8", DeviceTypeName.PAD)),
                                 ("Wacom Cintiq 22HDT Pen stylus           id: 13  type: STYLUS", ("Wacom Cintiq 22HDT Pen stylus", "13", DeviceTypeName.STYLUS)),
                                 ("Wacom Cintiq 22HDT Pen eraser           id: 14  type: ERASER", ("Wacom Cintiq 22HDT Pen eraser", "14", DeviceTypeName.ERASER)),
                                 ("Wacom Cintiq 22HDT Finger touch         id: 15  type: TOUCH", ("Wacom Cintiq 22HDT Finger touch", "15", DeviceTypeName.TOUCH)),
                                 ("Wacom Express Key Remote Pad pad        id: 17  type: PAD", ("Wacom Express Key Remote Pad pad", "17", DeviceTypeName.PAD)),
                                 ("Wacom Intuos Pro L Pad pad              id: 24  type: PAD", ("Wacom Intuos Pro L Pad pad", "24", DeviceTypeName.PAD)),
                                 ("Wacom Intuos Pro L Pen stylus           id: 25  type: STYLUS", ("Wacom Intuos Pro L Pen stylus", "25", DeviceTypeName.STYLUS)),
                                 ("Wacom Intuos Pro L Pen eraser           id: 26  type: ERASER", ("Wacom Intuos Pro L Pen eraser", "26", DeviceTypeName.ERASER)),
                                 ("Wacom Intuos Pro L Pen cursor           id: 27  type: CURSOR", ("Wacom Intuos Pro L Pen cursor", "27", DeviceTypeName.CURSOR)),
                                 ("Wacom Intuos Pro L Finger touch         id: 28  type: TOUCH", ("Wacom Intuos Pro L Finger touch", "28", DeviceTypeName.TOUCH)),
                                 ("  Wacom Intuos Pro L Finger touch       id: 28  type: TOUCH", ("Wacom Intuos Pro L Finger touch", "28", DeviceTypeName.TOUCH)),
                                 ("\tWacom Intuos Pro L Finger touch\t\t \tid:\t \t28\t  \ttype:\t \tTOUCH\t", ("Wacom Intuos Pro L Finger touch", "28", DeviceTypeName.TOUCH)),
                                 ("Wacom Intuos Pro L Finger touchid:28type:TOUCH", ("Wacom Intuos Pro L Finger touch", "28", DeviceTypeName.TOUCH)),
                                 ("Wacom Intuos Pro L Finger touch         id: 28  type: TOUCHx", None),
                                 ("Wacom Intuos Pro L Finger touch         id: 28  type: xTOUCH", None),
                                 ("Wacom Intuos Pro L Finger touch         id 28  type: TOUCH", None),
                                 ("Wacom Intuos Pro L Finger touch         xd: 28  type: TOUCH", None),
                             ])
    def test_parse_from_listing(self, item: str, expected_result: Optional[Tuple[str, str, DeviceTypeName]]):
        current_result = wacom._parse_device_from_listing(item)
        assert current_result == expected_result
