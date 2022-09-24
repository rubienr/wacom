# Configuration

The configuratin describes allows a more complete way to control the wacom board behaviour.
It turned out that Gnome 2/3 and KDE Plasma as of 2022 perform still very poor in this regards.
The user defined wacom board behaviour is achieved by the programs `xsetwacom` (behaviour), `XBindKeys` (tiggers 'xsetwacom.sh`) and scripting (`xsetwacom.sh`).


A configuration set consists of two files.
One file configures what parameters `xsetwacom` will set to the device.
The other tells `XBindKeys` how and when to trigger `xsetwacom.sh`.
This is mandatory for the wheel-button + LEDs (i.e. Intuous Pro) state and is handy if one button shall toggle the screen mapping (i.e. left screen, right screen, all screens).

## Naming Convention

Each cofig consists of two files:
- xsetwacom configuration (settings for buttons and pen)
- xbindkeys configuration (information how/when to trigger xsetwacom.sh)

Prefix of configuration file names should match but is not mandatory.
The postfix pattern is mandatory.
The recommended pattern is:

- <configuration-name>_xsetwacom.cfg
- <configuration-name>_xbindkeys.cfg

**Notes:**
- The <configuration-name> can be anything except `default` or `baseconfig` and must not contain '_'.
- The variable `XBINDKEYS_CFG_FILE` in `<configuration-name>_xsetwacom.cfg` must match the corresponding xsetwacom config file `<configuration-name>_xbindkeys.cfg`.

**Examples:**

- Krita
  - krita_xbindkeys.cfg
  - krita_xsetwacom.cfg # this cfg is mentioned in \*_xbindkeys.cfg
- Blender (sculpting)    
  - blender-sculpting_xsetwacom.cfg
  - blender-sculpting_xsetwacom.cfg
- Blender (2D animation)    
  - blender-2d-animation_xsetwacom.cfg
  - blender-2d-animation_sculpting_xsetwacom.cfg
