Config naming: `r"([A-Za-z0-9_]+)_config.py"`

Example:

```bash
$ ls ./configs 
__init__.py
krita_intuos_pro_config.py
__pycache__
readme.md
 
$ ./xsetwacom.py cfg --list
known configs:
  - krita_intuos_pro in /.../configs
```

New config Howto:

- duplicate another working configuration, i.e. `krita_intuos_pro_cofnig.py` → `myapp_mydevice_config.py`
- always derive your configuration class from `BaseConfig` and name it `Config` (mandatory)
- modify configuration
- test:
  ```bash
  $ ./xsetwacom.py cfg --list
  known configs:
    - krita_intuos_pro in /.../configs
    - myapp_mydevice in /.../configs
  ``` 
  ```bash
    $ ./xsetwacom.py --config myapp_mydevice cfg --print
    ...
  ```
  ```bash
    $ ./xsetwacom.py --config myapp_mydevice device --set
  ```
  ```bash
    $ ./xsetwacom.py --config myapp_mydevice bindkeys --start
  ```
