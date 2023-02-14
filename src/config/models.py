class WacomModel:
    device_hint: str = "-"
    device_note: str = "-"


class WacomExpressKeyRemotePad(WacomModel):
    device_hint: str = r"^Wacom Express Key Remote Pad .*"
    device_note: str = "BlueTooth remote with PAD input device (18 buttons + touch wheel and wheel LEDs)."


class WacomIntuosBT(WacomModel):
    device_hint: str = r"^Wacom Inutos BT .*"
    device_note: str = "USB/BlueTooth pen tablet with PAD (4 buttons) and STYLUS input devices."


class WacomIntuosPro(WacomModel):
    device_hint: str = r"^Wacom Intuos Pro .*"
    device_note: str = "USB/BlueTooth pen tablet with PAD (9 buttons + touch wheel and wheel LEDs), STYLUS, ERASER and TOUCH input devices."


class WacomCintiq22HDT(WacomModel):
    # Note: 22HD has no touch input whereas 22HDT has
    device_hint: str = r"^Wacom Cintiq 22HD(T)? .*"
    device_note: str = "Pen display with PAD (2x9 buttons and 2x1 touch sensitive scroll bar), STYLUS, ERASER and TOUCH (only 22HDT) input devices."


class WacomCintiq21UX(WacomModel):
    device_hint: str = r"^Wacom Cintiq 21UX .*"
    device_note: str = "Pen display with PAD (2x4 buttons and 2x1 touch sensitive scroll bar), STYLUS and ERASER device"


class WacomIntuos3Ptz430(WacomModel):
    device_hint: str = r"^Wacom Intuos3 4x5 .*"
    device_note: str = "4\"x5\" USB Pad with STYLUS, ERASER, PAD and CURSOR device"
