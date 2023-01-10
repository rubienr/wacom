import os.path
import pickle
import re
from enum import Enum
from typing import List, Optional, Tuple, Dict, Callable

from src.config.Env import LogLevel
from src.config.Env import instance as env
from src.geometry.types import Geometry, InputArea, Point
from src.utils.object_dump import object_dump
from src.utils.subprocess import lines_from_stream, run_subprocess
from src.wacom.DeviceInfo import DeviceInfo
from src.wacom.DeviceTypeName import DeviceTypeName
from src.wacom.get import get_devices_info


class AreaToOutputMappingMode(Enum):
    FULL_INPUT_AREA_FULL_DISPLAY = 1
    TRIMMED_INPUT_AREA_FULL_DISPLAY = 2
    UNKNOWN = 3


def get_display_geometries() -> List[str]:
    verbose = env.verbosity == LogLevel.DEBUG
    return lines_from_stream(run_subprocess("xrandr --listactivemonitors", verbose=verbose).stdout)


def parse_display_geometries(reported_geometries: List[str], verbose: bool = True) -> List[Geometry]:
    geometries = []
    for line in reported_geometries:
        # Example:
        # Monitors: 2
        #  0: +*DP-0 3840/609x2160/349+3840+0  DP-0
        #  1: +DP-2 3840/609x2160/349+0+0  DP-2
        re_match = re.match(r"\s*(\d+):\s*\+(\*?)\S*\s*(\d+)/(\d+)x(\d+)/(\d+)\+(\d+)\+(\d+)\s*(.*)", line)
        if re_match:
            geometries.append(
                Geometry(width_px=int(re_match.group(3)), height_px=int(re_match.group(5)),
                         width_mm=int(re_match.group(4)), height_mm=int(re_match.group(6)),
                         width_displacement_px=int(re_match.group(7)), height_displacement_px=int(re_match.group(8)),
                         idx=int(re_match.group(1)), is_primary=True if re_match.group(2) == "*" else False, name=re_match.group(9)))

    if verbose:
        print(f"detected {len(geometries)} geometries:")
        for geometry in geometries:
            print(f"  - {geometry.name}")
            print(object_dump(geometry, prefix="    "))

    assert len(geometries) > 0
    return geometries


def _next_geometry(temp_file_abs_path: str, temp_file_name: str, temp_file_suffix: str = ".geometry") -> Geometry:
    file_name = os.path.join(temp_file_abs_path, temp_file_name + temp_file_suffix)

    try:
        print(f"reading last geometry from '{file_name}' ...")
        temp_file = open(file_name, "rb")
        last_geometry = Geometry().from_dict(pickle.loads(temp_file.read()))
        temp_file.close()
    except (Exception,):
        print(f"failed to load pickled from file")
        default_geometry = Geometry()
        print("write default geometry:")
        print(object_dump(default_geometry, prefix="  "))
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
    geometries = parse_display_geometries(get_display_geometries())
    num_geometries = len(geometries)
    index = next_geometry_nr % num_geometries
    current_geometry = geometries[index]

    temp_file = open(file_name, "w+b")
    temp_file.truncate()
    temp_file.seek(0)
    pickle.dump(current_geometry.to_dict(), temp_file)
    temp_file.close()

    print(f"last geometry was {last_geometry.name}:")
    print(object_dump(last_geometry, prefix="  "))
    print(f"next geometry is {current_geometry.name}:")
    print(object_dump(current_geometry, prefix="  "))
    return current_geometry


def _compute_map_full_input_area_to_full_output(device_input_area: InputArea, output_geometry: Geometry) -> Tuple[Optional[InputArea], Optional[Geometry]]:
    full_input_area = device_input_area
    full_output_geometry = output_geometry
    return full_input_area, full_output_geometry


def _compute_trimmed_input_area_to_full_output(device_input_area: InputArea, output_geometry: Geometry) -> Tuple[Optional[InputArea], Optional[Geometry]]:
    full_input_area = device_input_area
    full_output_geometry = output_geometry

    # case 1) display width-to-height ratio equals device width-to-height ratio
    #  - map full display width to full device width
    #  - map full display height to full device height
    # case 2) display width-to-height ratio larger than device width-to-height ratio
    #  - map full display width to full device width
    #  - map full display height to reduced/scaled device height
    # case 3) display width-to-height ratio less than device width-to-height ratio
    #  - map full display width to reduced/scaled device width
    #  - map full display height to full device height

    if full_output_geometry.width_to_height_ratio > full_input_area.width_to_height_ratio:  # case 2)
        effective_input_height = full_input_area.width / full_output_geometry.width_px * full_output_geometry.height_px
        h_1 = int((full_input_area.height - effective_input_height) / 2)
        h_2 = h_1 + int(effective_input_height)
        trimmed_input_area = InputArea(Point(full_input_area.top_left.x, h_1), Point(full_input_area.bottom_right.x, h_2))
    elif full_output_geometry.width_to_height_ratio < full_input_area.width_to_height_ratio:  # case 3)
        effective_input_width = full_input_area.height / full_output_geometry.height_px * full_output_geometry.width_px
        w_1 = int((full_input_area.width - effective_input_width) / 2)
        w_2 = w_1 + int(effective_input_width)
        trimmed_input_area = InputArea(Point(w_1, full_input_area.top_left.y), Point(w_2, full_input_area.bottom_right.y))
    else:  # case 1)
        trimmed_input_area = full_input_area

    return trimmed_input_area, full_output_geometry


def _xsetwacom_set(device_id: str, args: str) -> None:
    command = f"xsetwacom --set {device_id.strip()} {args.strip()}"
    verbose = env.verbosity == LogLevel.DEBUG
    process = run_subprocess(command, verbose=verbose, check=True)
    lines_stdout = lines_from_stream(process.stdout)
    lines_stderr = lines_from_stream(process.stderr)
    for line in lines_stdout + lines_stderr:
        print(line)

    assert len(lines_stdout) == 0
    assert len(lines_stderr) == 0


def _set_input_area_and_output_mapping(devices_info: List[DeviceInfo], device_type: DeviceTypeName, input_area: InputArea, output_geometry: Geometry) -> None:
    for device_info in [dev_info for dev_info in devices_info if dev_info.dev_type == device_type]:
        area_args = f"Area {input_area.top_left.x} {input_area.top_left.y} {input_area.bottom_right.x} {input_area.bottom_right.y}"
        output_args = f"MapToOutput {output_geometry.width_px}x{output_geometry.height_px}{output_geometry.width_displacement_signed_str}{output_geometry.height_displacement_signed_str}"
        _xsetwacom_set(device_info.dev_id, area_args)
        _xsetwacom_set(device_info.dev_id, output_args)


def map_input_areas_to_output(device_hint_expression: str,
                              device_input_areas: Dict[DeviceTypeName, InputArea],
                              mode: AreaToOutputMappingMode,
                              device_calibration_overrides_config_input_area: bool,
                              temp_file_abs_path: str,
                              temp_file_name: str) -> None:
    geometry: Geometry = _next_geometry(temp_file_abs_path=temp_file_abs_path, temp_file_name=temp_file_name)
    method: Callable = {AreaToOutputMappingMode.FULL_INPUT_AREA_FULL_DISPLAY: _compute_map_full_input_area_to_full_output,
                        AreaToOutputMappingMode.TRIMMED_INPUT_AREA_FULL_DISPLAY: _compute_trimmed_input_area_to_full_output}[mode]

    device_types: List[DeviceTypeName] = [key for key in device_input_areas.keys()]
    print(f"mapping device input area of '{device_hint_expression}' for types {[t.name for t in device_types]} to display with strategy {mode.name} "
          f"and {'overridden' if device_calibration_overrides_config_input_area else 'configured'} input 'Area':")
    print("  - read default device input area: reset values")

    devices_info = get_devices_info(device_hint_expression, device_types=device_types, reset_device_and_read_input_area=device_calibration_overrides_config_input_area)
    device_input_areas_by_type = {}
    for info in devices_info:
        assert info.dev_type not in device_input_areas_by_type
        device_input_areas_by_type[info.dev_type] = info.input_area

    for dev_type, input_area in device_input_areas.items():
        if device_calibration_overrides_config_input_area:
            input_area = device_input_areas_by_type[dev_type]
        mapped_input_area, output_geometry = method(input_area, geometry)

        print(f"    - map device type {dev_type.name} to display:")
        print(f"    - from {'overridden' if device_calibration_overrides_config_input_area else 'configured'} input area:")
        print(object_dump(input_area, prefix="        "))
        print(f"    - to output display {output_geometry.name}:")
        print(object_dump(output_geometry, prefix="        "))
        print("    - with mapped input area:")
        print(object_dump(mapped_input_area, prefix="        "))

        _set_input_area_and_output_mapping(devices_info, dev_type, mapped_input_area, output_geometry)
