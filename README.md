# Quickly setting relevant Wacom settings

    $ xsetwacom.sh -h
    Usage: xsetwacom.sh [OPTION ...] 
    
     Options:
      -h, --help          Print this help.
      -m, --map [p|primary|s|seconary|a|all]
                          Map to primary secondary or all monitor(s) (as reported by xrandr).
                          Default: primary (2048x1280+0+0)
      -o, --mode          Absolute or Relative behaviour. Default: Absolute
      -c, --curve [x1 y1 x2 y2]
                          Set the pressure curve (3rd oder Bezier)
                          Default: 0 0 50 70
      -p, --parameters    Print all device parameters.


# Examples

    xsetwacom.sh -m p          # set mapping to primary monitor
    xsetwacom.sh -c 0 0 50 70  # set the pressure curve
    xsetwacom.sh -p            # print only supported parameters
    xsetwacom.sh -m p -c 0 0 50 70 -m Absolute
