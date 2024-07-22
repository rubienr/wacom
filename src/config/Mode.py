from typing import Callable, Any


class Mode:
    """
    Mode to getter/setter mapping.
    Required to support additional (LED independent) device modes:
      - devices without touch ring LEDs have no modes: this can simulate multiple modes
      - devices with touch: quickly switch touch functionality on/off
    """

    def __init__(self, name: str, getter: Callable[[], Any], setter: Callable[[], None]) -> None:
        self.name: str = name
        self.getter: Callable[[], None] = getter
        self.setter: Callable[[], None] = setter
