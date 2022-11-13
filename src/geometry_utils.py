import os.path
import pickle
import re
import subprocess
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple


class AreaToOutputMappingMode(Enum):
    FULL_INPUT_AREA_FULL_DISPLAY = 1,
    TRIMMED_INPUT_AREA_FULL_DISPLAY = 2,


class Geometry(object):
    def __init__(self,
                 width_px: int = 0, height_px: int = 0,
                 width_mm: int = 0, height_mm: int = 0,
                 width_displacement: int = 0, height_displacement: int = 0,
                 id: int = 0, name: str = ""):
        self.width_px: int = width_px
        self.height_px: int = height_px
        self.width_mm: int = width_mm
        self.height_mm: int = height_mm
        self.width_displacement: int = width_displacement
        self.height_displacement: int = height_displacement
        self.id: int = id
        self.name: str = name

    def to_dict(self) -> Dict[str, Any]:
        return vars(self)

    def from_dict(self, from_attrs: Dict[str, Any]) -> "Geometry":
        for key in from_attrs:
            attr_typet = type(self.__dict__[key])  # preserve type as dict will always have string values
            setattr(self, key, attr_typet(from_attrs[key]))
        return self


# ============================================================ section: run command

def _run_subprocess(args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, **kwargs)


def _lines_from_stream(lines_stream):
    return str(lines_stream.strip()).split('\n') if len(lines_stream) > 0 else []


# ============================================================ section: geometry

def get_display_geometries() -> List[Geometry]:
    lines = _lines_from_stream(_run_subprocess("xrandr --listactivemonitors").stdout)
    geometries = []

    for line in lines:
        # Example:
        # Monitors: 2
        #  0: +*DP-0 3840/609x2160/349+3840+0  DP-0
        #  1: +DP-2 3840/609x2160/349+0+0  DP-2
        re_match = re.match(r"\s*(\d+):\s*\+\*?\S*\s*(\d+)/(\d+)x(\d+)/(\d+)\+(\d+)\+(\d+)\s*(.*)", line)
        if re_match:
            geometries.append(
                Geometry(width_px=re_match.group(2), height_px=re_match.group(4),
                         width_mm=re_match.group(3), height_mm=re_match.group(5),
                         width_displacement=re_match.group(6), height_displacement=re_match.group(7),
                         id=re_match.group(1), name=re_match.group(8)))

    return geometries


def _next_geometry(temp_file_abs_path: str, temp_file_name: str = ".geometry.tmp") -> Geometry:
    file_name = os.path.join(temp_file_abs_path, temp_file_name)

    try:
        print(f"reading last geometry from '{file_name}' ...")
        temp_file = open(file_name, "rb")
        last_geometry = Geometry().from_dict(pickle.loads(temp_file.read()))
        temp_file.close()
    except:
        print(f"failed to load pickled from file")
        default_geometry = Geometry()
        print(f"write default: {default_geometry.to_dict()}")
        temp_file = open(file_name, "w+b")
        temp_file.truncate()
        temp_file.seek(0)
        pickle.dump(default_geometry.to_dict(), temp_file)
        temp_file.close()

        print(f"re-reading last geometry from '{file_name}' ...")
        temp_file = open(file_name, "rb")
        last_geometry = Geometry().from_dict(pickle.loads(temp_file.read()))
        temp_file.close()

    next_geometry_nr = 1 + last_geometry.id
    geometries = get_display_geometries()
    num_geometries = len(geometries)
    x = next_geometry_nr % num_geometries
    current_geometry = geometries[x]

    temp_file = open(file_name, "w+b")
    temp_file.truncate()
    temp_file.seek(0)
    pickle.dump(current_geometry.to_dict(), temp_file)
    temp_file.close()

    print(f"last geometry {last_geometry.to_dict()}")
    print(f"next geometry {current_geometry.to_dict()}")
    return current_geometry


class Point(object):
    def __init__(self, x: int = 0, y: int = 0):
        self.x: int = x
        self.y: int = y


class InputArea(object):
    def __init__(self, top_left: Point, bottom_right: Point):
        self.top_left = top_left
        self.bottom_right = bottom_right


class OutputArea(Geometry):
    def __init__(self,
                 width_px: int = 0, height_px: int = 0,
                 width_mm: int = 0, height_mm: int = 0,
                 width_displacement: int = 0, height_displacement: int = 0,
                 id: int = 0, name: str = ""):
        super().__init__(width_px, height_px, width_mm, height_mm, width_displacement, height_displacement, id, name)


def _compute_input_area_output_mapping(mode: AreaToOutputMappingMode, geometry: Geometry) -> Tuple[Optional[InputArea], Optional[OutputArea]]:
    # TODO compute mapping
    return (InputArea(Point(0, 0), Point(62200, 43200)),
            OutputArea(geometry.width_px, geometry.height_px,
                       width_mm=0, height_mm=0,
                       width_displacement=0,
                       height_displacement=0,
                       id=geometry.id))


def map_area_to_output(_device_hint_expression: str, mode: AreaToOutputMappingMode, temp_file_abs_path: str) -> None:
    geometry: Geometry = _next_geometry(temp_file_abs_path)
    _compute_input_area_output_mapping(mode, geometry)
    # TODO set input area and map to output
    assert False
