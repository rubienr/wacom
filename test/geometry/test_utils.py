from typing import List

import pytest

import src.geometry.utils
from src.geometry.types import Geometry, InputArea, Point


class TestGeometry:

    @pytest.mark.parametrize(
        "reported_geometries, expected_geometries",
        [
            (["Monitors: 99\n",
              "0: +*DP-2 3840/609x2160/349+1920+0  DP-2\n"],
             [Geometry(width_px=3840, height_px=2160, width_mm=609, height_mm=349, width_displacement_px=1920, height_displacement_px=0, idx=0, is_primary=True, name="DP-2")]),
            (["Monitors: 99\n",
              "0: +*DP-2 3840/609x2160/349+1920+0  DP-2\n",
              "1: +DP-5 1920/476x1080/268+0+1080  DP-5\n"],
             [Geometry(width_px=3840, height_px=2160, width_mm=609, height_mm=349, width_displacement_px=1920, height_displacement_px=0, idx=0, is_primary=True, name="DP-2"),
              Geometry(width_px=1920, height_px=1080, width_mm=476, height_mm=268, width_displacement_px=0, height_displacement_px=1080, idx=1, is_primary=False, name="DP-5")]),
            (["Monitors: 99",
              "0: +DP-2 3840/609x2160/349+1920+0  DP-2",
              "1: +*DP-5 1920/476x1080/268+0+1080  DP-5",
              "2: +DP-0 3840/609x2160/349+5760+0  DP-0"],
             [Geometry(width_px=3840, height_px=2160, width_mm=609, height_mm=349, width_displacement_px=1920, height_displacement_px=0, idx=0, is_primary=False, name="DP-2"),
              Geometry(width_px=1920, height_px=1080, width_mm=476, height_mm=268, width_displacement_px=0, height_displacement_px=1080, idx=1, is_primary=True, name="DP-5"),
              Geometry(width_px=3840, height_px=2160, width_mm=609, height_mm=349, width_displacement_px=5760, height_displacement_px=0, idx=2, is_primary=False, name="DP-0")]),
            (["",
              "0: +DP-2 3840/609x2160/349+1920+0  DP-2\n"],
             [Geometry(width_px=3840, height_px=2160, width_mm=609, height_mm=349, width_displacement_px=1920, height_displacement_px=0, idx=0, is_primary=False, name="DP-2")]),
            (["0:\t  \t+*DP-2\t  \t3840/609x2160/349+1920+0\t  \tDP-2\n"],
             [Geometry(width_px=3840, height_px=2160, width_mm=609, height_mm=349, width_displacement_px=1920, height_displacement_px=0, idx=0, is_primary=True, name="DP-2")]),
            (["Monitors: 99",
              "0: +*DP-2 3840/609x2160/349+1920+0  DP-2",
              "1: +*DP-5 1920/476x1080/268+0+1080  DP-5",
              "2: +*DP-0 3840/609x2160/349+5760+0  DP-0"],
             [Geometry(width_px=3840, height_px=2160, width_mm=609, height_mm=349, width_displacement_px=1920, height_displacement_px=0, idx=0, is_primary=True, name="DP-2"),
              Geometry(width_px=1920, height_px=1080, width_mm=476, height_mm=268, width_displacement_px=0, height_displacement_px=1080, idx=1, is_primary=True, name="DP-5"),
              Geometry(width_px=3840, height_px=2160, width_mm=609, height_mm=349, width_displacement_px=5760, height_displacement_px=0, idx=2, is_primary=True, name="DP-0")]),
        ])
    def test_get_display_geometries(self, reported_geometries: List[str], expected_geometries: List[Geometry]):
        current_geometries = src.geometry.utils.parse_display_geometries(reported_geometries, verbose=False)
        assert len(current_geometries) == len(expected_geometries)

        for current, expected in zip(current_geometries, expected_geometries):
            assert current == expected


class TestGeometryMapping:

    @pytest.mark.parametrize(
        "input_area, output_geometry, expected_mapped_input_area, expected_mapped_output_geometry",
        [
            # base: input dimension == output dimension
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=100, height_px=100, width_displacement_px=0, height_displacement_px=0),
             InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=100, height_px=100, width_displacement_px=0, height_displacement_px=0)),

            # output width is larger than input width
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=101, height_px=100, width_displacement_px=0, height_displacement_px=0),
             InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=101, height_px=100, width_displacement_px=0, height_displacement_px=0)),

            # output width is smaller than input width
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=99, height_px=100, width_displacement_px=0, height_displacement_px=0),
             InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=99, height_px=100, width_displacement_px=0, height_displacement_px=0)),

            # output height is larger than input height
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=100, height_px=101, width_displacement_px=0, height_displacement_px=0),
             InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=100, height_px=101, width_displacement_px=0, height_displacement_px=0)),

            # output height is smaller than input height
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=100, height_px=99, width_displacement_px=0, height_displacement_px=0),
             InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=100, height_px=99, width_displacement_px=0, height_displacement_px=0)),
        ])
    def test_compute_map_full_input_area_to_full_output(self,
                                                        input_area: InputArea,
                                                        output_geometry: Geometry,
                                                        expected_mapped_input_area: InputArea,
                                                        expected_mapped_output_geometry: Geometry):
        current_mapped_input_area, current_mapped_output_geometry = src.geometry.utils._compute_map_full_input_area_to_full_output(input_area, output_geometry)
        assert current_mapped_input_area is not None
        assert current_mapped_output_geometry is not None
        assert current_mapped_output_geometry == expected_mapped_output_geometry
        assert current_mapped_input_area == expected_mapped_input_area

    @pytest.mark.parametrize(
        "input_area, output_geometry, "
        "expected_mapped_input_area, expected_mapped_output_geometry",
        [
            # I)
            # input:   square
            # display: square
            # expect:  maximize input width and height

            # I.a) input == geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=100, height_px=100),
             InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=100, height_px=100)),
            # I.b) input <  geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=200, height_px=200),
             InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=200, height_px=200)),
            # I.c) input >  geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=50, height_px=50),
             InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=50, height_px=50)),

            # II)
            # input:   square
            # display: landscape
            # expect:  maximize input width, scale and center input height

            # II.a) input <= geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=200, height_px=100),
             InputArea(top_left=Point(0, 25), bottom_right=Point(100, 75)), Geometry(width_px=200, height_px=100)),
            # II.b) input <= geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=100, height_px=50),
             InputArea(top_left=Point(0, 25), bottom_right=Point(100, 75)), Geometry(width_px=100, height_px=50)),
            # II.c) input <  geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=400, height_px=200),
             InputArea(top_left=Point(0, 25), bottom_right=Point(100, 75)), Geometry(width_px=400, height_px=200)),
            # II.d) input >  geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(100, 100)), Geometry(width_px=50, height_px=25),
             InputArea(top_left=Point(0, 25), bottom_right=Point(100, 75)), Geometry(width_px=50, height_px=25)),

            # II)
            # input:   landscape
            # display: square
            # expect:  maximize input height, scale and center input width

            # III.a) input >= geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=100, height_px=100),
             InputArea(top_left=Point(50, 0), bottom_right=Point(150, 100)), Geometry(width_px=100, height_px=100)),
            # III.b) input <=  geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=200, height_px=200),
             InputArea(top_left=Point(50, 0), bottom_right=Point(150, 100)), Geometry(width_px=200, height_px=200)),
            # III.c) input >  geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=50, height_px=50),
             InputArea(top_left=Point(50, 0), bottom_right=Point(150, 100)), Geometry(width_px=50, height_px=50)),
            # III.d) input <  geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=400, height_px=400),
             InputArea(top_left=Point(50, 0), bottom_right=Point(150, 100)), Geometry(width_px=400, height_px=400)),

            # IV)
            # input:   landscape
            # display: landscape

            # IV.a)
            #   ratio:   input_width_to_height == display_width_to_height
            #   expect:  maximize input width and height

            # IV.a.1) input == geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=200, height_px=100),
             InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=200, height_px=100)),
            # IV.a.2) input >  geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=50, height_px=25),
             InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=50, height_px=25)),
            # IV.a.3) input <  geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=400, height_px=200),
             InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=400, height_px=200)),

            # IV.b)
            #   ratio:   input_width_to_height <  display_width_to_height
            #   expect:  maximize input width, scale and center input height

            # IV.b.1) input <= geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=400, height_px=100),
             InputArea(top_left=Point(0, 25), bottom_right=Point(200, 75)), Geometry(width_px=400, height_px=100)),
            # IV.b.2) input >= geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=100, height_px=25),
             InputArea(top_left=Point(0, 25), bottom_right=Point(200, 75)), Geometry(width_px=100, height_px=25)),
            # IV.b.3) input < geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=800, height_px=200),
             InputArea(top_left=Point(0, 25), bottom_right=Point(200, 75)), Geometry(width_px=800, height_px=200)),
            # IV.b.4) input > geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(200, 100)), Geometry(width_px=40, height_px=10),
             InputArea(top_left=Point(0, 25), bottom_right=Point(200, 75)), Geometry(width_px=40, height_px=10)),

            # IV.c)
            #   ratio:   input_width_to_height >  display_width_to_height
            #   expect:  maximize input height, scale and center input width
            # IV.c.1) input <= geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(400, 100)), Geometry(width_px=200, height_px=100),
             InputArea(top_left=Point(100, 0), bottom_right=Point(300, 100)), Geometry(width_px=200, height_px=100)),
            # IV.c.2) input >= geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(400, 100)), Geometry(width_px=200, height_px=100),
             InputArea(top_left=Point(100, 0), bottom_right=Point(300, 100)), Geometry(width_px=200, height_px=100)),
            # IV.c.3) input <  geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(400, 100)), Geometry(width_px=200, height_px=100),
             InputArea(top_left=Point(100, 0), bottom_right=Point(300, 100)), Geometry(width_px=200, height_px=100)),
            # IV.c.4) input >  geometry
            (InputArea(top_left=Point(0, 0), bottom_right=Point(400, 100)), Geometry(width_px=200, height_px=100),
             InputArea(top_left=Point(100, 0), bottom_right=Point(300, 100)), Geometry(width_px=200, height_px=100))
        ], )
    def test_compute_trimmed_input_area_to_full_output(self,
                                                       input_area: InputArea,
                                                       output_geometry: Geometry,
                                                       expected_mapped_input_area: InputArea,
                                                       expected_mapped_output_geometry: Geometry):
        current_mapped_input_area, current_mapped_output_geometry = src.geometry.utils._compute_trimmed_input_area_to_full_output(input_area, output_geometry)
        assert current_mapped_input_area is not None
        assert current_mapped_output_geometry is not None
        assert current_mapped_input_area == expected_mapped_input_area
        assert current_mapped_output_geometry == expected_mapped_output_geometry
