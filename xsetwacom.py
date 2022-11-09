#!/bin/env python3
import argparse
import os

from src.ConfigLoader import ConfigLoader
from src.DeviceTypeName import DeviceTypeName
from src.geometry_utils import AreaToOutputMappingMode, map_area_to_output
from src.tablet_config_utils import configure_devices, print_all_device_parameters
from src.tablet_utils import print_devices, plot_pressure_curve, plot_current_pressure, get_device_id, get_devices_id
from src.xbindkeys_utils import run_xbindkeys


class Env(object):
    def __init__(self):
        self.script_dir = os.path.dirname(__file__)
        self.configs_path_name = "configs"


class Args(object):
    def __init__(self, env: Env, config_loader: ConfigLoader):
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        layout_group = parser.add_argument_group("Digitizer")
        layout_group.add_argument("-d", "--devices",
                                  help="list devices (i.e. stylus, eraser, touch, pad)",
                                  action="store_true")
        layout_group.add_argument("-p", "--parameter",
                                  help="List all current device(s) parameter by device-id (digitizer must be attached). Device '-' denotes any device.",
                                  choices=(["-"] + get_devices_id(".*", DeviceTypeName.ANY)))
        layout_group.add_argument("-w", "--xsetwacom",
                                  help="Applies configuration to digitizer; see --config",
                                  action="store_true")
        layout_group.add_argument("-g", "--geometry",
                                  help="Modifies the input area according to the current display geometry."
                                       "next: map to next display, input area is trimmed to retain horizontal vs. vertical proportions;"
                                       "next_scale: map to next display, input area mapped to output (causes distortion width:height ratio of display is not same as digitizer ratio)",
                                  choices=(["next", "next_scale"]),
                                  default="next")

        export_group = parser.add_argument_group("Xbindkeys (start, stop, reload)")
        export_group.add_argument("-x", "--xbindkeys",
                                  help="Start (fg, bg) 'xbindkeys' and run in foreground (fg), detach to background (bg), kill (ki) running instances or reload (re) configuration."
                                       "Xbindkeys will intercept mouse/key events ant trigger actions accordingly. "
                                       "Applies Xbindkeys configuration as specified by --config."
                                       "Does not change device parameters.",
                                  choices=["fg", "bg", "re", "ki"],
                                  default="fg")

        config_group = parser.add_argument_group("Configuration")
        config_group.add_argument("-c", "--config",
                                  help="Apply given configuration for the current run.",
                                  choices=[c.config_name for c in config_loader.config_names()],
                                  default="krita_intuos_pro")
        config_group.add_argument("-s", "--configs",
                                  help="list known configurations",
                                  action="store_true")
        config_group.add_argument("-r", "--print",
                                  help="print configuration",
                                  choices=[c.config_name for c in config_loader.config_names()])

        config_group = parser.add_argument_group("Pressure Curve")
        config_group.add_argument("-u", "--curve",
                                  help="Plot the configured pressure curve and the resulting Bezier curve (requires gnuplot).",
                                  action="store_true")
        config_group.add_argument("-e", "--pressure",
                                  help="Live plot the current pressure curve (requires xinput and feedgnuplot). The pressure plot does not appear until the first pressure value is reported.",
                                  action="store_true")

        self.args: argparse.Namespace = parser.parse_args()

        if self.args.configs:
            print("configs:")
            for config_name in config_loader.config_names():
                print(f"  - {config_name.config_name} in {os.path.join(env.script_dir, env.configs_path_name)}")
            exit(0)


def run():
    env = Env()
    config_loader = ConfigLoader(env.script_dir, env.configs_path_name)
    args = Args(env, config_loader).args

    if args.devices:
        print_devices()
    elif args.parameter:
        device_id = None if args.parameter == "-" else args.parameter
        print_all_device_parameters(device_id)
    elif args.print:
        config_loader.load_config(args.print)
        config_loader.config.print_config()
    elif args.curve:
        config_loader.load_config(args.config)
        config = config_loader.config
        plot_pressure_curve(config.pressure_curve[DeviceTypeName.STYLUS])
    elif args.pressure:
        config_loader.load_config(args.config)
        config = config_loader.config
        device_id = get_device_id(config.device_hint_expression, DeviceTypeName.STYLUS)
        assert device_id
        plot_current_pressure(device_id)
    elif args.xsetwacom:
        config_loader.load_config(args.config)
        config = config_loader.config
        configure_devices(config)
    elif args.geometry:
        config_loader.load_config(args.config)
        config = config_loader.config
        map_area_to_output(config.device_hint_expression, AreaToOutputMappingMode.TRIMMED_INPUT_AREA_FULL_DISPLAY)
    elif args.xbindkeys:
        config_loader.load_config(args.config)
        config = config_loader.config
        run_xbindkeys(config.xbindkeys_config_string, args.xbindkeys)


if __name__ == "__main__":
    run()
