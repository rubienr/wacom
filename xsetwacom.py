#!/bin/env python3
import argparse
import os

from configs.base_config import DeviceConfigType
from src.ConfigLoader import ConfigLoader
from src.tablet_utils import print_devices, get_device_ids, print_all_device_parameters_by_device, print_all_device_parameters, plot_pressure_curve, plot_current_pressure, get_stylus_device_ids, \
    configure_device
from src.xbindkeys_utils import run_xbindkeys


class Env(object):
    def __init__(self):
        self.script_dir = os.path.dirname(__file__)
        self.configs_path_name = "configs"


class Args(object):
    def __init__(self, env: Env, config_loader: ConfigLoader):
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        layout_group = parser.add_argument_group("Device")
        layout_group.add_argument("-d", "--devices",
                                  help="list devices",
                                  action="store_true")
        layout_group.add_argument("-p", "--parameter",
                                  help="list all current device(s) parameter (device must be attached)",
                                  choices=(["-"] + get_device_ids(".*")))

        export_group = parser.add_argument_group("Xbindkeys")
        export_group.add_argument("-x", "--xbindkeys",
                                  help="start xbindkeys and run in foreground (does not touch tablet parameters)",
                                  action="store_true")
        export_group.add_argument("-b", "--background",
                                  help="send xbindkeys in background (with -x or --xbindkeys)",
                                  action="store_true")

        config_group = parser.add_argument_group("Configuration")
        config_group.add_argument("-c", "--config",
                                  help="apply configuration.",
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
        if "-" == args.parameter:
            print_all_device_parameters_by_device()
        else:
            print_all_device_parameters(args.parameter)
    elif args.print:
        config_loader.load_config(args.print)
        config_loader.config.print_config()
    elif args.curve:
        config_loader.load_config(args.config)
        config = config_loader.config
        plot_pressure_curve(config.pressure_curve[DeviceConfigType.STYLUS])
    elif args.pressure:
        config_loader.load_config(args.config)
        config = config_loader.config
        device_ids = get_stylus_device_ids(config.device_hint_expression)
        assert len(device_ids) == 1
        device_id = device_ids[0]
        plot_current_pressure(device_id)
    elif args.xbindkeys:
        config_loader.load_config(args.config)
        config = config_loader.config
        run_xbindkeys(config.xbindkeys_config_string, run_in_background=args.background is not None)
    else:
        config_loader.load_config(args.config)
        config = config_loader.config
        configure_device(config)


if __name__ == "__main__":
    run()
