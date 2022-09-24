# Configuration

The configuration allows a more complete way to control the wacom board behaviour.
It turned out that Gnome 2/3 and KDE Plasma as of 2022 perform still very poor in this regards.
The user defined Wacom board behaviour is achieved by

- `xsetwacom` (behaviour), 
- `XBindKeys` (tiggers `xsetwacom.sh`) and 
- scripting (`xsetwacom.sh`).

A configuration set always consists of two files.
One file configures what parameters `xsetwacom` will send to the device.
The other tells `XBindKeys` how and when to trigger `xsetwacom.sh`.
This is mandatory for the wheel-button and LEDs state (i.e. Intuous Pro) but is also handy if one button shall cycle through the screen mapping (left, right, both).

## Naming Convention

Each config consists of two files:
- `xsetwacom` configuration (buttons and pen settings)
- `xbindkeys` configuration (information how/when `xsetwacom.sh` is triggered)

The prefix of related configuration files should match but is not mandatory to do so.
However, the postfix pattern is fixed and mandatory.

Recommended pattern is:

- \<configuration-name\>_xsetwacom.cfg
- \<configuration-name\>_xbindkeys.cfg

**Notes:**
- The `<configuration-name>` can be anything except 'default' or 'baseconfig' and must not contain '_'.
- The variable `XBINDKEYS_CFG_FILE` in `<configuration-name>_xsetwacom.cfg` must match the corresponding xsetwacom config file `<configuration-name>_xbindkeys.cfg`.

**Examples:**

- Krita
  - krita_xsetwacom.cfg
  - krita_xbindkeys.cfg
- Blender (sculpting)    
  - blender-sculpting_xsetwacom.cfg
  - blender-sculpting_xbindkeys.cfg
- Blender (2D animation)    
  - blender-2d-animation_xsetwacom.cfg
  - blender-2d-animation_xbindkeys.cfg
