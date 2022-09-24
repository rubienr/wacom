# Configuration

The configuration allows a more complete way to control the wacom board behaviour.
It turned out that Gnome 2/3 and KDE Plasma as of 2022 perform still very poor in this regards.
The user defined Wacom board behaviour is achieved by the

- `xsetwacom` (behaviour), 
- `XBindKeys` (tiggers 'xsetwacom.sh') and 
- scripting (`xsetwacom.sh`).

A configuration set consists always of two files.
One file configures what parameters `xsetwacom` will send to the device.
The other tells `XBindKeys` how and when to trigger `xsetwacom.sh`.
This is mandatory for the wheel-button and LEDs state (i.e. Intuous Pro) but is handy if one button shall sycle through the screen mapping (left, right, both).

## Naming Convention

Each cofig consists of two files:
- `xsetwacom` configuration (settings for buttons and pen)
- `xbindkeys` configuration (information how/when to trigger `xsetwacom.sh`)

The prefix of related configuration files should match but is not mandatory.
The postfix pattern is mandatory.

Recommended pattern is:

- <configuration-name>_xsetwacom.cfg
- <configuration-name>_xbindkeys.cfg

**Notes:**
- The `<configuration-name>` can be anything except 'default' or 'baseconfig' and must not contain '_'.
- The variable `XBINDKEYS_CFG_FILE` in `<configuration-name>_xsetwacom.cfg` must match the corresponding xsetwacom config file `<configuration-name>_xbindkeys.cfg`.

**Examples:**

- Krita
  - krita_xbindkeys.cfg
  - krita_xsetwacom.cfg
- Blender (sculpting)    
  - blender-sculpting_xsetwacom.cfg
  - blender-sculpting_xsetwacom.cfg
- Blender (2D animation)    
  - blender-2d-animation_xsetwacom.cfg
  - blender-2d-animation_sculpting_xsetwacom.cfg
