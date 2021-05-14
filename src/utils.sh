#!/bin/env bash

# ============================ section config ==========================


# qinput  ... nothing
# @stdout ... space separated list of all found configuration names
# @return ... $?
function get_config_names()
{
    pushd $SCRIPT_PATH/configs > /dev/null 2>&1
    while read cfg_file ; do
        echo -en "$(echo "$cfg_file" | grep -v "baseconfig-" | cut --delimiter='-' --fields=1) "
    done <<< "$(ls *xsetwacom.cfg 2>&1)" |xargs
    popd > /dev/null 2>&1
}


## @stdout   ... nothing
## @input $1 ... config name
## @return   ... $?
#function try_load_config()
#{
#    local config_name=$1
#    local base_config_file=baseconfig-xsetwacom.cfg
#    local config_file=${config_name}-xsetwacom.cfg
#
#    pushd $SCRIPT_PATH/configs > /dev/null 2>&1
#    source $base_config_file
#    source $config_file
#    popd > /dev/null 2>&1
#}


# @stdout ... nothing
# @input  ... nothing
# @exit   ... 1 on error
# @return ... $?
function load_base_config()
{
    local config_file=baseconfig-xsetwacom.cfg
    
    pushd $SCRIPT_PATH/configs > /dev/null 2>&1
    if ! source $config_file > /dev/null 2>&1 ; then
        echo "Loading base configuration \"config_file\" failed."
        exit 1
    fi
    popd > /dev/null 2>&1
}


# @stdout   ... nothing
# @input $1 ... config name
# @exit     ... 1 on error
# @return   ... $?
function load_config()
{
    local config_name=$1
    local config_file=${config_name}-xsetwacom.cfg
    
    pushd $SCRIPT_PATH/configs > /dev/null 2>&1
    if ! source $config_file > /dev/null 2>&1 ; then
        echo "Loading configuration \"config_file\" failed."
        exit 1
    fi
    popd > /dev/null 2>&1
}


# @stdout ... the default config name
# @return ... $?
function get_default_config_name()
{
    local config_names=($(get_config_names))
    echo ${config_names[0]}
}

# @stdout   ... the formatted associated array 
# @input $1 ... associative array (variable name)
# @input $2 ... indentation
# @return   ... $?
function _print_associative_array()
{
    local array_name=$1
    declare -n aarray=$1
    local identation=$2

    echo "$identation$array_name (${#aarray[@]})"
    for key in "${!aarray[@]}" ; do
      local value=${aarray[$key]}
      echo "$identation$identation[$key] = \"$value\""
    done

    unset -n aarray
}

# @stdout ... the configuration values
# @input  ... $1 identation
# @return ... $?
function print_loaded_config()
{
    local identation=$1
    local config_variables=(
        "PAD_DEVICE_IDS"
        "STYLUS_DEVICE_IDS"
        "ERASER_DEVICE_IDS"
        "XBINDKEYS_CFG"
    )
    local config_arrays=(
        "ALL_PARAMETERS"
        "PAD_PARAMETERS"
        "PAD_BUTTON_MAPPING"
        "STYLUS_PARAMETERS"
        "STYLUS_BUTTON_MAPPING"
        "ERASER_PARAMETERS"
        "ERASER_BUTTON_MAPPING"
    )
    
    for config_var_name in "${config_variables[@]}" ; do
        declare -n ref=$config_var_name
        echo "$identation$config_var_name = \"$ref\""
        unset -n ref
    done
    
    for config_array_name in "${config_arrays[@]}" ; do
      _print_associative_array "$config_array_name" "$identation"
    done
}

# ========================== section geometry ==========================



# @stdout ... space separated list of geometries in one line (whole screen, primary screen, secondary screen)
# @exit   ... extit 1 if not all geometries could be parsed
# @return ... $?
function get_geometries()
{
    local whole_geometry=""
    local primary_geometry=""
    local secondary_geometry=""

    local xrandr_lines=$(xrandr --query)
    while read xrandr_line ; do
        # example output:
        # Screen 0: minimum 8 x 8, current 4096 x 1280, maximum 16384 x 16384                              <--- whole geometry
        # DVI-I-0 disconnected (normal left inverted right x axis y axis)
        # DVI-I-1 disconnected (normal left inverted right x axis y axis)
        # DVI-I-2 connected primary 2048x1280+0+0 (normal left inverted right x axis y axis) 610mm x 350mm <--- primary geometry
        # HDMI-0 disconnected (normal left inverted right x axis y axis)
        # DVI-I-3 connected 2048x1280+2048+0 (normal left inverted right x axis y axis) 610mm x 350mm      <--- secondary geometry

        local wg=$(echo "$xrandr_line" | grep --perl-regex --only-matching "(?<=, current )\s*[0-9x ]*\s*(?=, maximum )")
        local pg=$(echo "$xrandr_line" | grep --perl-regex --only-matching "(?<= connected primary )\s*[0-9x+]*")
        local sg=$(echo "$xrandr_line" | grep --perl-regex --only-matching "(?<= connected )\s*[0-9x+]*")

        if [ -n "$wg" ] ; then
            wg=$(echo $wg | tr -d "\r\n " && echo -n "+0+0")
            whole_geometry=$wg
        elif [ -n "$pg" ] ; then
            primary_geometry=$pg
        elif [ -n "$sg" ] ; then
            secondary_geometry=$sg
        fi
    done <<< "$xrandr_lines"

    if [ -z "$whole_geometry" -o -z "$primary_geometry" -o -z "$secondary_geometry" ] ; then
        exit 1
    fi

    echo "$whole_geometry $primary_geometry $secondary_geometry"
}


# ========================== section devices ==========================


# @stdout   ... verbose device list
# @input $1 ... identation
# @return   ... $?
function print_devices()
{
    local identation=$1
    local lines=$(xsetwacom --list)

    while read line ; do
        echo "$identation$line"
    done <<< "$lines"
}


# @stdout ... the device number
# @input  ... none
# @return ... $?
function _grep_device_id()
{
    grep --perl-regex --only-matching "(?<=id: )\s*[0-9]*\s*(?=type:)" | tr "\n" " " | tr -d "\t\r" | xargs
}

# @stdout ... all device numbers, space separated
# @input  ... none
# @return ... $?
function get_all_device_ids()
{
    xsetwacom --list devices | _grep_device_id
}


# @stdout ... all pad device numbers, space separated
# @input  ... none
# @return ... $?
function get_all_pad_device_ids()
{
    xsetwacom --list devices | grep "pad" | _grep_device_id
}


# @stdout ... all stylus device numbers, space separated
# @input ... none
# @return ... $?
function get_all_stylus_device_ids()
{
    xsetwacom --list devices | grep "stylus" | _grep_device_id
}


# @stdout ... all eraser device numbers, space separated
# @input ... none
# @return ... $?
function get_all_eraser_device_ids()
{
    xsetwacom --list devices | grep "eraser" | _grep_device_id
}


# @input $1 ... identation
# @stdout   ... all connected devices' supported parameters
# @return   ... $?
function print_all_devices_parameters()
{
    local identation=$1
    for device_id in $(get_all_device_ids) ; do
        echo "${identation}Device $device_id parameters"
        local lines=$(xsetwacom --shell --get $device_id all 2>&1 | grep -v "does not exist")
        while read line ; do
          echo "$identation$identation$line"
        done <<< "$lines"
    done
}


# @input $1 ... device id
# @input $2 ... button mapping (config array name)
# @input $3 ... identation
# @stdout   ... xsetwacom output
# @return   ... $?
function set_button_mapping()
{
    local device_id=$1
    #local array_name=$2
    declare -n buttons=$2
    local identation=$3
    
    #echo "$identation$array_name (${#aarray[@]})"
    for button in "${!buttons[@]}" ; do
        local value=${buttons[$button]}
        echo -en "$identation$identation$button = \"$value\"\n"
        xsetwacom --set $device_id $button $value 2>&1 | awk '{ print "${identation}${identation}" $0 }'
    done

    unset -n aarray
}


# @input $1 ... device id
# @input $2 ... parameters mapping (config array name)
# @input $3 ... identation
# @stdout   ... xsetwacom output
# @return   ... $?
function set_device_parameters()
{
    local device_id=$1
    local array_name=$2
    declare -n parameters=$2
    local identation=$3

    for parameter in "${!parameters[@]}" ; do
        local value=${parameters[$parameter]}
        echo -e "$identation$parameter = \"$value\""
        xsetwacom --set $device_id $parameter $value 2>&1 | awk -v idnt="$identation" '{ print idnt""idnt""$0 }'
    done
}


# @input  ... nothing
# @stdout ... log on exit, nothing otherwise
# @exit   ... 1 on error
# @return ... 0 otherwise
function exit_if_no_device_found()
{
    if [ "x" == "x$(get_all_device_ids)" ] ; then
        echo -en "\nNo device found.\n"
        exit 1
    fi
    return 0
}


# @pre    ... XSETWACOM_PARAMS_OLD was updated
# @input  ... nothing
# @stdout ... diff of XSETWACOM_PARAMS_OLD and print_all_devices_parameters
# @return ... $?
function print_effective_changes()
{
    local xsewacom_params_new=$(print_all_devices_parameters)
    local effective_changes=$(diff <(echo "$XSETWACOM_PARAMS_OLD") <(echo "$xsewacom_params_new") && echo "xsetwacom reported no changes" )

    echo "$effective_changes" | awk -v idnt="$identation$identation" '{ print idnt""$0 }'
}


# @pre    ... device is connected
# @input  ... nothing
# @stdout ... all libwacom-list-local-devices lines containing "android mode"
# @return ... 0
function warn_if_device_in_android_mode()
{
    local devices=$(libwacom-list-local-devices | grep -i "android mode" | grep --perl-regex --only-matching "(?<==).*")

    if [ -n "$devices" ] ; then
        echo "Warning: found device(s) in android mode:"
        echo "$devices" | awk -v idnt="  " '{ print idnt""idnt""$0 }'
        echo
    fi
    return 0
}


# ======================== section key bindings ========================


# @pre      ... cofiguration is loaded
# @input $1 ... start/stop mode: daemon, nodaemon, kill
# @stdout   ... verbose device list
# @exit     ... 1 on invalid input
# @return   ... $?
function bind_keys()
{
    local mode=$1

    case $mode in
        daemon)
            echo "bind keys with $SCRIPTPATH./configs/$XBINDKEYS_CFG_FILE (running in background)"
            xbindkeys --file "$SCRIPTPATH./configs/$XBINDKEYS_CFG_FILE" > /dev/null 2>&1
        ;;
        nodaemon)
            echo "bind keys with $SCRIPTPATH./configs/$XBINDKEYS_CFG_FILE"
            xbindkeys --file "$SCRIPTPATH./configs/$XBINDKEYS_CFG_FILE" --verbose --nodaemon
        ;;
        kill)
            killall xbindkeys
            instances=$(ps aux | grep xbindkeys | grep -Ev "grep|$SCRIPTNMAE")
            if [ "x" != "x$instances" ] ; then
                echo "Still instances found after stopping xbindkeys:"
                echo "$instances"
            fi
        ;;
        reload)
            killall -HUP xbindkeys
        ;;
        *)
        echo "Failed to manipulate xbindkeys in mode \"$mode\""
        exit 1
        ;;
    esac
}
