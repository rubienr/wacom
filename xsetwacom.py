#!/bin/env python3
import argparse
import os

from src.ConfigLoader import ConfigLoader
from src.DeviceTypeName import DeviceTypeName
from src.base_config import BaseConfig
from src.geometry_utils import AreaToOutputMappingMode, map_area_to_output
from src.tablet_config_utils import configure_devices, print_all_device_parameters
from src.tablet_utils import print_devices, plot_pressure_curve, plot_current_pressure, get_device_id, get_devices_id
from src.xbindkeys_utils import xbindkeys_start_foreground, xbindkeys_start_background, xbindkeys_reload_config_from_disk, xbindkeys_killall


class Env(object):
    def __init__(self):
        self.script_abs_dir = os.path.dirname(__file__)
        self.configs_rel_path_name = "configs"
        self.tmp_files_abs_dir = self.script_abs_dir


class Args(object):
    def __init__(self, config_loader: ConfigLoader):
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        sub_parsers = self.parser.add_subparsers(dest='command', title="command (required)", description="Run command with the loaded configuration.")

        sp = sub_parsers.add_parser("device",
                                    help="detect devices; set and get device parameter",
                                    description="Digitizer specific actions (see also 'xsetwacom --help').")
        g = sp.add_mutually_exclusive_group()
        g.add_argument("-l", "--list",
                       help="List all discovered devices (i.e. attached: stylus, eraser, touch, pad).",
                       action="store_true")
        g.add_argument("-s", "--set",
                       help="Applies loaded configuration to the digitizer.",
                       action="store_true")
        g.add_argument("-m", "--map",
                       help="Modifies the device input area according to the current display geometry. "
                            "'next': map to next display, input area is trimmed to retain horizontal vs. vertical proportions. "
                            "'next_scale': map to next display, input area mapped to output (causes distortion width:height ratio of display is not same as digitizer ratio)",
                       choices=(["next", "next_scale"]),
                       default="next")
        g.add_argument("-p", "--parameter",
                       help="List all current device(s) parameter by device-id (digitizer must be attached). Device '-' denotes any device.",
                       choices=(["-"] + get_devices_id(".*", DeviceTypeName.ANY)))

        sp = sub_parsers.add_parser("bindkeys",
                                    help="bind device-key events to system mouse/keyboard events",
                                    description="Xbindkeys will intercepts device-events and triggers system mouse/key events accordingly "
                                                "(see also 'man xbindkeys').")
        g = sp.add_mutually_exclusive_group()
        g.add_argument("-s", "--start",
                       help="Start Xbindkeys and run in foreground (press CTRL+C to stop).",
                       action="store_true")
        g.add_argument("-b", "--background",
                       help="Start Xbindkeys and run detached to background.",
                       action="store_true")
        g.add_argument("-r", "--reload",
                       help="Tell running Xbindkeys instances to reload configuration from disk without restarting the process.",
                       action="store_true")
        g.add_argument("-k", "--kill",
                       help="Kills running Xbindkeys instances.")

        sub_group = self.parser.add_argument_group("Configuration",
                                                   description="Load and provide the configuration to the command.")
        g = sub_group.add_mutually_exclusive_group()
        g.add_argument("-c", "--config",
                       help="Loads the given configuration by name.",
                       choices=[c.config_name for c in config_loader.config_names()],
                       default="krita_intuos_pro")

        sp = sub_parsers.add_parser("cfg",
                                    help="print known configurations or configuration values",
                                    description="Print configuration names or read and print values of a specific configuration.")
        g = sp.add_mutually_exclusive_group()
        g.add_argument("-l", "--list",
                       help="List known configurations name and exit.",
                       action="store_true")
        g.add_argument("-p", "--print",
                       help="Print configuration values and exit.",
                       action="store_true")

        sp = sub_parsers.add_parser("plot",
                                    help="Visualize pressure curve or current pressure.",
                                    description="Visualizes the pressure curve (static) or the current pressure (live).")
        g = sp.add_mutually_exclusive_group()
        g.add_argument("-c", "--curve",
                       help="Plot the configured pressure curve and the resulting Bezier curve (requires gnuplot).",
                       action="store_true")
        g.add_argument("-p", "--pressure",
                       help="Live plot the current pressure curve (requires xinput and feedgnuplot). "
                            "The pressure plot does not appear until the first pressure value is reported.",
                       action="store_true")
        sp.add_argument("-d", "--device",
                        help="The pressure device.",
                        choices=[DeviceTypeName.STYLUS.name, DeviceTypeName.ERASER.name],
                        default=DeviceTypeName.STYLUS.name)

        self.args: argparse.Namespace = self.parser.parse_args()


class Runner(object):
    def __init__(self):
        self.env = Env()
        self.config_loader = ConfigLoader(self.env.script_abs_dir, self.env.configs_rel_path_name)
        self._cli_args = Args(self.config_loader)
        self._config = None

    @property
    def args(self):
        return self._cli_args.args

    @property
    def parser(self):
        return self._cli_args.parser

    @property
    def config(self) -> BaseConfig:
        if not self._config:
            self.config_loader.load_config(self.args.config)
            self._config = self.config_loader.config
        return self._config

    def run(self) -> int:

        if not self.args.command:
            self.parser.print_help()
            return 1

        if self.args.command == "cfg":
            if self.args.list:
                print("known configs:")
                for config_name in self.config_loader.config_names():
                    print(f"  - {config_name.config_name} in {os.path.join(self.env.script_abs_dir, self.env.configs_rel_path_name)}")
            if self.args.print:
                self.config.print_config()

        if self.args.command == "device":
            if self.args.list:
                print_devices()
            if self.args.set:
                configure_devices(self.config)
            if self.args.map:
                map_area_to_output(self.config.device_hint_expression, AreaToOutputMappingMode.TRIMMED_INPUT_AREA_FULL_DISPLAY, self.env.tmp_files_abs_dir)
            if self.args.parameter:
                device_id = None if self.args.parameter == "-" else self.args.parameter
                print_all_device_parameters(device_id)

        if self.args.command == "bindkeys":
            if self.args.start:
                xbindkeys_start_foreground(self.config.xbindkeys_config_string)
            if self.args.background:
                xbindkeys_start_background(self.config.xbindkeys_config_string)
            if self.args.reload:
                xbindkeys_reload_config_from_disk()
            if self.args.kill:
                xbindkeys_killall()

        if self.args.command == "plot":
            device: DeviceTypeName = DeviceTypeName[self.args.device]
            if self.args.curve:
                try:
                    curve = self.config.devices_parameters[device].args["PressureCurve"].split(" ")
                    curve_points = ((curve[0], curve[1]), (curve[2], curve[3]))
                    plot_pressure_curve(curve_points)
                except:
                    print(f"WARNING: no curve configured for device '{self.args.device}'")
            if self.args.pressure:
                plot_current_pressure(get_device_id(self.config.device_hint_expression, device))

        return 0


if __name__ == "__main__":
    exit(Runner().run())
