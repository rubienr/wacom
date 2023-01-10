from typing import Tuple

from src.config.Env import LogLevel
from src.config.Env import instance as env
from src.utils.subprocess import run_subprocess


def plot_pressure_curve(two_points: Tuple[Tuple[int, int], Tuple[int, int]]) -> None:
    """
    requires gnuplot
    """
    plot_data = f"0 0\\n{two_points[0][0]} {two_points[0][1]}\\n{two_points[1][0]} {two_points[1][1]}\\n100 100\\n"
    print("bezier pressure curve control points:\nx y")
    print(f"{plot_data}")
    # TODO - pythonic way
    # TODO - fix plot
    command = f"echo -e \"{plot_data}e\\n\" " \
              f"| tee -a /dev/stdout " \
              f"| gnuplot -p -e \"set grid; plot '-' using 1:2 smooth bezier title 'pressure curve', '' using 1:2 with linespoints pointtype 3 title 'control points'\""

    verbose = env.verbosity == LogLevel.DEBUG
    if verbose:
        print(command)

    run_subprocess(command, verbose=verbose)


def plot_current_pressure(device_id: str) -> None:
    """
    requires xinput and feedgnuplot

    Note: In theory device_id as reported by xsetwacom should match device id from xinput; if not - workaround::

       device_info=`xinput --list | grep -i "Pen stylus"`
       declare -a device_ids
       device_ids=(`echo "$device_info" | grep -i "$device_hint" | grep --perl-regexp --only-matching "(?<=id=).*(?=\[)" | tr --delete "[:blank:]"`)
       device_id=${device_ids[0]}

    :param device_id: device id as reported by xinput/xsetwacom
    """
    # TODO - pythonic way
    command = f"xinput --test \"{device_id}\" " \
              r"| awk -F '[[:blank:]]*a\\[[[:digit:]]+\\]=' '{ if ($4 > 0) {print $4 ; fflush()} }' " \
              "| feedgnuplot --exit --stream 0.25 --y2 1 --lines --unset grid --xlen 1000 --ymin 0 --ymax 65536 --y2min 0 --y2max 65536"
    verbose = env.verbosity == LogLevel.DEBUG
    run_subprocess(command, verbose=verbose)
