import os.path
import pickle
import re
from enum import Enum
from typing import List, Optional, Tuple

from src.geometry.types import Geometry, InputArea, Point
from src.utils.subprocess import lines_from_stream, run_subprocess
from src.wacom.DeviceTypeName import DeviceTypeName
from src.wacom.get import get_devices_info


class AreaToOutputMappingMode(Enum):
    FULL_INPUT_AREA_FULL_DISPLAY = 1,
    TRIMMED_INPUT_AREA_FULL_DISPLAY = 2,
    UNKNOWN = 3,


def get_display_geometries(verbose: bool = True) -> List[Geometry]:
    lines = lines_from_stream(run_subprocess("xrandr --listactivemonitors").stdout)
    geometries = []

    for line in lines:
        # Example:
        # Monitors: 2
        #  0: +*DP-0 3840/609x2160/349+3840+0  DP-0
        #  1: +DP-2 3840/609x2160/349+0+0  DP-2
        re_match = re.match(r"\s*(\d+):\s*\+\*?\S*\s*(\d+)/(\d+)x(\d+)/(\d+)\+(\d+)\+(\d+)\s*(.*)", line)
        if re_match:
            geometries.append(
                Geometry(width_px=int(re_match.group(2)), height_px=int(re_match.group(4)),
                         width_mm=int(re_match.group(3)), height_mm=int(re_match.group(5)),
                         width_displacement_px=int(re_match.group(6)), height_displacement_px=int(re_match.group(7)),
                         idx=re_match.group(1), name=re_match.group(8)))

        min_width_displacement, max_width_displacement = Geometry(), Geometry()
        min_height_displacement, max_height_displacement = Geometry(), Geometry()

        if len(geometries) == 2:
            # 1st geometry: left most display
            # 2nd geometry: right most display
            # 3rd geometry: left + right display; works only with 2 horizontally or vertically aligned displays and same size
            for geometry in geometries:
                if geometry.width_displacement_px > min_width_displacement.width_displacement_px:
                    max_width_displacement = geometry
                elif geometry.width_displacement_px < max_width_displacement.width_displacement_px:
                    min_width_displacement = geometry

                if geometry.height_displacement_px > min_height_displacement.height_displacement_px:
                    max_height_displacement = geometry
                elif geometry.height_displacement_px < max_height_displacement.height_displacement_px:
                    min_height_displacement = geometry

            geometries.append(Geometry(width_px=(max_width_displacement.width_displacement_px + max_width_displacement.width_px) - min_width_displacement.width_displacement_px,
                                       height_px=(max_height_displacement.height_displacement_px + max_width_displacement.height_px) - min_height_displacement.height_displacement_px,
                                       width_mm=-1, height_mm=-1,
                                       width_displacement_px=0, height_displacement_px=0,
                                       idx=len(geometries), name="virtual-geometry"))

    if verbose:
        print("detected geometries:")
        for g in geometries:
            print(f"  - {g.to_dict()}")

    assert len(geometries) > 0
    return geometries


def _next_geometry(temp_file_abs_path: str, temp_file_name: str = ".geometry.tmp") -> Geometry:
    file_name = os.path.join(temp_file_abs_path, temp_file_name)

    try:
        print(f"reading last geometry from '{file_name}' ...")
        temp_file = open(file_name, "rb")
        last_geometry = Geometry().from_dict(pickle.loads(temp_file.read()))
        temp_file.close()
    except (Exception,):
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

    next_geometry_nr = 1 + last_geometry.idx
    geometries = get_display_geometries()
    num_geometries = len(geometries)
    x = next_geometry_nr % num_geometries
    current_geometry = geometries[x]

    temp_file = open(file_name, "w+b")
    temp_file.truncate()
    temp_file.seek(0)
    pickle.dump(current_geometry.to_dict(), temp_file)
    temp_file.close()

    print(f"last geometry was {last_geometry.to_dict()}")
    print(f"next geometry is {current_geometry.to_dict()}")
    return current_geometry


def _compute_map_full_input_area_to_full_output(device_input_area: InputArea, output_geometry: Geometry) -> Tuple[Optional[InputArea], Optional[Geometry]]:
    full_input_area = device_input_area
    full_output_geometry = output_geometry
    return full_input_area, full_output_geometry


def _compute_trimmed_input_area_to_full_output(device_input_area: InputArea, output_geometry: Geometry) -> Tuple[Optional[InputArea], Optional[Geometry]]:
    full_input_area = device_input_area
    full_output_geometry = output_geometry

    # case 1) display width-to-height ratio larger than device display-to-height ratio
    #  - map full display width to full device width
    #  - map full display height to reduced/scaled device height
    # case 2) display width-to-height ratio less than device display-to-height ratio
    #  - map full display width to reduced/scaled device width
    #  - map full display height to full device height
    # case 3) display width-to-height ratio equals device display-to-height ratio
    #  - map full display width to full device width
    #  - map full display height to full device height

    if full_output_geometry.width_to_height_ratio > full_input_area.width_to_height_ratio:  # case 1)
        effective_input_height = full_input_area.width / full_output_geometry.width_px * full_output_geometry.height_px
        h1 = int((full_input_area.height - effective_input_height) / 2)
        h2 = h1 + int(effective_input_height)
        trimmed_input_area = InputArea(Point(full_input_area.top_left.x, h1), Point(full_input_area.bottom_right.x, h2))
    elif full_output_geometry.width_to_height_ratio < full_input_area.width_to_height_ratio:  # case 2)
        effective_input_width = full_input_area.height / full_output_geometry.height_px * full_output_geometry.width_px
        w1 = int((full_input_area.width - effective_input_width) / 2)
        w2 = w1 + int(effective_input_width)
        trimmed_input_area = InputArea(Point(w1, full_input_area.top_left.y), Point(w2, full_input_area.bottom_right.y))
    else:  # case 3)
        trimmed_input_area = full_input_area

    return trimmed_input_area, full_output_geometry


def _xsetwacom_set(device_id: str, args: str, verbose: bool = True) -> None:
    command = f"xsetwacom --set {device_id.strip()} {args.strip()}"
    if verbose:
        print(command)
    process = run_subprocess(command, check=True)
    lines_stdout = lines_from_stream(process.stdout)
    lines_stderr = lines_from_stream(process.stderr)
    for line in lines_stdout + lines_stderr:
        print(line)

    assert len(lines_stdout) == 0
    assert len(lines_stderr) == 0


def _set_input_area_and_output_mapping(device_hint_expression: str, input_area: InputArea, output_geometry: Geometry) -> None:
    print(f"map device input area: {input_area.to_dict()}")
    print(f"of device: {device_hint_expression}")
    print(f"to display output geometry: {output_geometry.to_dict()}")

    for device_id, _device_type, _info in get_devices_info(device_hint_expression, [DeviceTypeName.STYLUS, DeviceTypeName.ERASER, DeviceTypeName.TOUCH]):
        area_args = f"Area {input_area.top_left.x} {input_area.top_left.y} {input_area.bottom_right.x} {input_area.bottom_right.y}"
        output_args = f"MapToOutput {output_geometry.width_px}x{output_geometry.height_px}{output_geometry.width_displacement_signed_str}{output_geometry.height_displacement_signed_str}"
        _xsetwacom_set(device_id, area_args)
        _xsetwacom_set(device_id, output_args)


def map_area_to_output(device_hint_expression: str, device_input_area: InputArea, mode: AreaToOutputMappingMode, temp_file_abs_path: str) -> None:
    geometry: Geometry = _next_geometry(temp_file_abs_path)

    if mode == AreaToOutputMappingMode.FULL_INPUT_AREA_FULL_DISPLAY:
        input_area, output_geometry = _compute_map_full_input_area_to_full_output(device_input_area, geometry)
    elif mode == AreaToOutputMappingMode.TRIMMED_INPUT_AREA_FULL_DISPLAY:
        input_area, output_geometry = _compute_trimmed_input_area_to_full_output(device_input_area, geometry)
    else:
        assert False

    _set_input_area_and_output_mapping(device_hint_expression, input_area, output_geometry)
