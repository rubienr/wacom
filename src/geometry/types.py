from typing import Dict, Any


class Geometry(object):
    def __init__(self,
                 width_px: int = 0, height_px: int = 0,
                 width_mm: int = 0, height_mm: int = 0,
                 width_displacement_px: int = 0, height_displacement_px: int = 0,
                 idx: int = 0, name: str = "") -> None:
        """

        :param width_px:
        :param height_px:
        :param width_mm:
        :param height_mm:
        :param width_displacement_px: 0 is left most
        :param height_displacement_px: 0 is top most
        :param idx: arbitrary nr for sorting; no duplicates
        :param name: as reported by `xrandr --listactivemonitors`
        """
        self.width_px: int = width_px
        self.height_px: int = height_px
        self.width_mm: int = width_mm
        self.height_mm: int = height_mm
        self.width_displacement_px: int = width_displacement_px
        self.height_displacement_px: int = height_displacement_px
        self.idx: int = idx
        self.name: str = name

    def to_dict(self) -> Dict[str, Any]:
        return vars(self)

    def from_dict(self, from_attrs: Dict[str, Any]) -> "Geometry":
        for key in from_attrs:
            attr_typet = type(self.__dict__[key])  # preserve type as dict will always have string values
            setattr(self, key, attr_typet(from_attrs[key]))
        return self

    @property
    def width_to_height_ratio(self) -> float:
        return self.width_px / self.height_px

    @property
    def width_displacement_signed_str(self) -> str:
        return f"+{self.width_displacement_px}" if self.width_displacement_px >= 0 else f"{self.width_displacement_px}"

    @property
    def height_displacement_signed_str(self) -> str:
        return f"+{self.height_displacement_px}" if self.height_displacement_px >= 0 else f"{self.height_displacement_px}"


class Point(object):
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x: int = x
        self.y: int = y

    def to_dict(self) -> Dict[str, Any]:
        return vars(self)


class SquareArea(object):
    def __init__(self, top_left: Point, bottom_right: Point, width_displacement: int = 0, height_displacement: int = 0) -> None:
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.width_displacement = width_displacement
        self.height_displacement = height_displacement

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        for key, value in vars(self).items():
            d[key] = value.to_dict() if hasattr(value, "to_dict") else value
        return d

    @property
    def width(self) -> int:
        return self.bottom_right.x - self.top_left.x

    @property
    def height(self) -> int:
        return self.bottom_right.y - self.top_left.y

    @property
    def width_to_height_ratio(self) -> float:
        return self.width / self.height


class InputArea(SquareArea):
    def __init__(self, top_left: Point, bottom_right: Point) -> None:
        super().__init__(top_left, bottom_right)
