#!/bin/env python3
import argparse

from src.config.BaseConfig import BaseConfig
from src.config.ConfigLoader import ConfigLoader
from src.config.Env import LogLevel
from src.config.Env import instance as env
from src.geometry.utils import AreaToOutputMappingMode, map_input_areas_to_output
from src.wacom.DeviceTypeName import DeviceTypeName
from src.wacom.get import get_device_id, get_devices_id, print_all_device_parameters, print_devices
from src.wacom.plot import plot_current_pressure, plot_pressure_curve
from src.wacom.set import configure_devices
from src.xbindkeys.utils import xbindkeys_reload_config_from_disk, xbindkeys_killall, xbindkeys_start


class Args:
    def __init__(self, config_loader: ConfigLoader) -> None:
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        sub_parsers = self.parser.add_subparsers(dest='command', title="command (required)", description="Run command with the loaded configuration.")

        sup = sub_parsers.add_parser("device",
                                     help="detect devices; set and get device parameter",
                                     description="Digitizer specific actions (see also 'xsetwacom --help').")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument("-l", "--list",
                         help="List all discovered devices (i.e. attached: stylus, eraser, touch, pad).",
                         action="store_true")
        grp.add_argument("-s", "--set",
                         help="Applies loaded configuration to the digitizer.",
                         action="store_true")
        grp.add_argument("-m", "--map",
                         help="Updates the device parameters 'Area' (input area of Wacom device) and 'MapToOutput' (output area of display). "
                              "Subsequent calls cycle through available displays and update the mapping. "
                              "The configured input area is assumed to be the device physical input resolution."
                              "'keep' keeps the width:height input ratio (by clipping 'Area') in sync with the output width:height ratio. "
                              "'keepo' is similar to 'keep' but overrides the input area from the configuration with the device's factory default value. "
                              "'scale' simply scales the device input 'Area' to the display output area. Depending on both resolutions this may lead to a stretch or a squeeze effect. "
                              "'scaleo' is similar to 'scale' but overrides the configured input area in the same way 'keepo' does.",
                         choices=(["keep", "keepo", "scale", "scaleo"]))
        grp.add_argument("-p", "--parameter",
                         help="List all current device(s) parameter by device-id (digitizer must be attached). Device '-' denotes any device.",
                         choices=(["-"] + get_devices_id(".*", DeviceTypeName.ANY)))

        sup = sub_parsers.add_parser("bindkeys",
                                     help="bind device-key events to system mouse/keyboard events",
                                     description="Xbindkeys will intercepts device-events and triggers system mouse/key events accordingly "
                                                 "(see also 'man xbindkeys').")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument("-s", "--start",
                         help="Start Xbindkeys and run in foreground (press CTRL+C to stop).",
                         action="store_true")
        grp.add_argument("-b", "--background",
                         help="Start Xbindkeys and run detached in background.",
                         action="store_true")
        grp.add_argument("-r", "--reload",
                         help="Tell running Xbindkeys instances to reload configuration from disk without restarting the process.",
                         action="store_true")
        grp.add_argument("-k", "--kill",
                         help="Kills running Xbindkeys instances.",
                         action="store_true")

        sup = sub_parsers.add_parser("mode",
                                     help="manipulate device modes, i.e. for devices without LED indicators",
                                     description="Toggle list or print modes' state. "
                                                 "Modes are persistent in between runs; multiple modes are supported.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument("-t", "--toggle",
                         help="Toggle in between mode states: i.e. for devices without LEDs. Multiple modes are supported. "
                              "The modes are persisted in between runs. For possible choices run with 'mode --list'.")
        grp.add_argument("-l", "--list",
                         help="Lists all known modes for the given configuration.",
                         action="store_true")
        grp.add_argument("-p", "--print",
                         help="Prints the current value of the requested mode.", )

        sub_group = self.parser.add_argument_group("Configuration",
                                                   description="Load and provide the configuration to the command.")
        grp = sub_group.add_mutually_exclusive_group()
        grp.add_argument("-c", "--config",
                         help="Loads the given configuration by name.",
                         choices=[c.config_name for c in config_loader.config_names()],
                         default="krita_intuos_pro")

        sub_group = self.parser.add_argument_group("Logging",
                                                   description="Manipulate the verbosity level.")
        grp = sub_group.add_mutually_exclusive_group()
        grp.add_argument("-l", "--log",
                         help="Set the logging level: lesser logs INFO, verbose DEBUG.",
                         choices=[v.name for v in LogLevel],
                         default=LogLevel.INFO.name)

        sup = sub_parsers.add_parser("config",
                                     help="print known configurations or configuration values",
                                     description="Print configuration names or read and print values of a specific configuration.")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument("-l", "--list",
                         help="List known configurations name and exit.",
                         action="store_true")
        grp.add_argument("-p", "--print",
                         help="Print configuration values and exit.",
                         action="store_true")

        sup = sub_parsers.add_parser("plot",
                                     help="Visualize pressure curve or current pressure.",
                                     description="Visualizes the pressure curve (static) or the current pressure (live).")
        grp = sup.add_mutually_exclusive_group()
        grp.add_argument("-c", "--curve",
                         help="Plot the configured pressure curve and the resulting Bezier curve (requires gnuplot).",
                         action="store_true")
        grp.add_argument("-p", "--pressure",
                         help="Live plot the current pressure curve (requires xinput and feedgnuplot). "
                              "The pressure plot does not appear until the first pressure value is reported.",
                         action="store_true")
        sup.add_argument("-d", "--device",
                         help="The pressure device.",
                         choices=[DeviceTypeName.STYLUS.name, DeviceTypeName.ERASER.name],
                         default=DeviceTypeName.STYLUS.name)

        self.args: argparse.Namespace = self.parser.parse_args()


class Runner:
    def __init__(self) -> None:
        self.env = env
        self.config_loader: ConfigLoader = ConfigLoader(self.env.script_abs_path, self.env.configs_rel_path_name)
        self._cli_args: Args = Args(self.config_loader)
        self.env.verbosity = LogLevel[self.args.log]

    @property
    def args(self):
        return self._cli_args.args

    @property
    def parser(self):
        return self._cli_args.parser

    @property
    def config(self) -> BaseConfig:
        if not self.config_loader.config:
            self.config_loader.load_config(self.args.config)
        return self.config_loader.config

    def run(self) -> int:

        if not self.args.command:
            self.parser.print_help()
            return 1

        if self.args.command == "config":
            if self.args.list:
                print("known configs:")
                for config_name in self.config_loader.config_names():
                    print(f"  - {config_name.config_name} in {self.env.configs_abs_path_name}")
            if self.args.print:
                self.config.print_config()

        if self.args.command == "device":
            if self.args.list:
                print_devices()
            if self.args.set:
                configure_devices(self.config)
            if self.args.map:
                mode = AreaToOutputMappingMode.TRIMMED_INPUT_AREA_FULL_DISPLAY if self.args.map in ["keep", "keepo"] else AreaToOutputMappingMode.FULL_INPUT_AREA_FULL_DISPLAY
                override = self.args.map in ["keepo", "scaleo"]
                map_input_areas_to_output(device_hint_expression=self.config.device_hint_expression,
                                          device_input_areas=self.config.device_input_areas,
                                          mode=mode,
                                          device_calibration_overrides_config_input_area=override,
                                          temp_file_abs_path=self.env.tmp_files_abs_path,
                                          temp_file_name=self.config.name)
            if self.args.parameter:
                device_id = None if self.args.parameter == "-" else self.args.parameter
                print_all_device_parameters(device_id)

        if self.args.command == "bindkeys":
            if self.args.start:
                xbindkeys_start(config=self.config.xbindkeys_config_string, temp_path=self.env.tmp_files_abs_path, config_file_name=self.config.name)
            if self.args.background:
                xbindkeys_start(config=self.config.xbindkeys_config_string, temp_path=self.env.tmp_files_abs_path, config_file_name=self.config.name, run_in_background=True)
            if self.args.reload:
                xbindkeys_reload_config_from_disk()
            if self.args.kill:
                xbindkeys_killall()

        if self.args.command == "mode":
            known_modes = self.config.modes.keys()
            if self.args.list:
                print(f"found {len(known_modes)} supported mode(s) for config '{self.config.name}':")
                for mode in known_modes:
                    print(f"  - {mode}")
            if self.args.print:
                requested_mode = self.args.print
                if requested_mode not in known_modes:
                    print(f"unknown mode '{requested_mode}', found {len(known_modes)} supported mode(s):")
                    for mode in known_modes:
                        print(f"  - {mode}")
                else:
                    print(f"status of mode '{requested_mode}' from config '{self.config.name}':")
                    print(f"{self.config.modes[requested_mode].getter()}")
            if self.args.toggle:
                requested_mode = self.args.toggle
                if requested_mode not in known_modes:
                    print(f"unknown mode '{requested_mode}', found {len(known_modes)} supported mode(s):")
                    for mode in known_modes:
                        print(f"  - {mode}")
                else:
                    self.config.modes[requested_mode].setter()
                    print(f"{self.config.modes[requested_mode].getter()}")

        if self.args.command == "plot":
            device: DeviceTypeName = DeviceTypeName[self.args.device]
            if self.args.curve:
                try:
                    curve = self.config.devices_parameters[device].args["PressureCurve"][0].split(" ")
                    curve_points = ((int(curve[0]), int(curve[1])), (int(curve[2]), int(curve[3])))
                    plot_pressure_curve(curve_points)
                except (Exception,):
                    print(f"WARNING: no curve configured for device '{self.args.device}'")
            if self.args.pressure:
                device_id = get_device_id(self.config.device_hint_expression, device)
                if device_id is not None:
                    plot_current_pressure(device_id)
                else:
                    print(f"ERROR: failed to plot pressure of device '{self.args.device}'")
                    assert False

        return 0


if __name__ == "__main__":
    exit(Runner().run())
