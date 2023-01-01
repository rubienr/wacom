Config naming: `r"([A-Za-z0-9_]+)_config.py"`

Example:

```bash
$ ls ./configs 
__init__.py
krita_intuos_pro_config.py
readme.md
 
$ ./xsetwacom.py config --list
known configs:
  - krita_intuos_pro in /.../configs
  - ...
```

New config how-to:

1. Duplicate a working configuration. 
2. Always derive the configuration class from `BaseConfig` and name it `Config` (mandatory)
3. Modify the configuration.
4. Test:
   ```bash
   $ ./xsetwacom.py config --list
   known configs:
     - krita_intuos_pro in /.../configs
     - myapp_mydevice in /.../configs
     - ...
   ``` 
   ```bash
     $ ./xsetwacom.py --config myapp_mydevice config --print
     ...
   ```
   ```bash
     $ ./xsetwacom.py --config myapp_mydevice device --set
     ...
   ```
   ```bash
     $ ./xsetwacom.py --config myapp_mydevice bindkeys --start
     ...
   ```
