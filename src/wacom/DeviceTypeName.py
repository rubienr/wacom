from enum import Enum


class DeviceTypeName(Enum):
    PAD = "PAD"  # buttons, wheel and scroll stripe
    STYLUS = "STYLUS"  # front tip of the stylus including buttons (if any)
    ERASER = "ERASER"  # rear end of the stylus (if any)
    CURSOR = "CURSOR"  # ??
    TOUCH = "TOUCH"  # finger/gesture touch sensitive device (inf any)
    ANY = "ANY"  # refers to any device type
    UNKNOWN = "unknown"
