import re
import subprocess
from enum import Enum
from typing import List, Union


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


def get_next_geometry(last_geometry: Union[int, Geometry]) -> Geometry:
    next_geometry_nr = 1 + (last_geometry.id if isinstance(last_geometry, Geometry) else last_geometry)
    geometries = get_display_geometries()
    num_geometries = len(geometries)
    x = next_geometry_nr % num_geometries
    return geometries[x]


def map_area_to_output(device_hint_expression: str, mode: AreaToOutputMappingMode) -> None:
    # TODO
    # read last geometry nr from file or default to 0
    last_geometry_nr = 0
    next_geometry = get_next_geometry(last_geometry_nr)
    # save last geometry to file and close
    # compute input area and map
    assert False
