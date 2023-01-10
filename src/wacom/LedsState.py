from typing import Dict, List


class LedsState:

    def __init__(self, intensities: List[int]) -> None:
        self.intensities: List[int] = intensities

    def on_off_states(self) -> Dict[int, bool]:
        """
        :return: Dict mapping from LED number to on-off state; True == on (intensity > 0), else False == off
        """
        return {idx: self.intensities[idx] > 0 for idx in range(0, len(self.intensities))}

    def active_led_number(self, default_on_error: int = 99) -> int:
        """
        :param default_on_error: default return value on error
        :return: number of first touch-ring LED found to be on, -1 otherwise
        """
        for led_nr, is_on in self.on_off_states().items():
            if is_on:
                return led_nr
        return default_on_error
