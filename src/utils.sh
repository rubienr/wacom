#!/bin/env bash

# ============================ section config ==========================


# qinput  ... nothing
# @stdout ... space separated list of all found configuration names
# @return ... $?
function get_config_names()
{
    pushd $SCRIPT_PATH/configs > /dev/null 2>&1
    while read cfg_file ; do
        echo -en "$(echo "$cfg_file" | grep -v "baseconfig_" | cut --delimiter='_' --fields=1) "
    done <<< "$(ls *_xsetwacom.cfg 2>&1)" |xargs
    popd > /dev/null 2>&1
}


# @stdout ... nothing
# @input  ... nothing
# @exit   ... 1 on error
# @return ... $?
function load_base_config()
{
    local config_file="baseconfig_xsetwacom.cfg"
    
    pushd $SCRIPT_PATH/configs > /dev/null 2>&1
    if ! source $config_file > /dev/null 2>&1 ; then
        echo "Loading base configuration \"$config_file\" failed."
        exit 1
    fi
    popd > /dev/null 2>&1
}


# @stdout ... nothing
# @input  ... $1 config name
# @exit   ... 1 on error
# @return ... $?
function load_config()
{
    local config_name="$1"
    local config_file="${config_name}_xsetwacom.cfg"
    
    pushd $SCRIPT_PATH/configs > /dev/null 2>&1
    if ! source $config_file > /dev/null 2>&1 ; then
        echo "Loading configuration \"$config_file\" failed."
        exit 1
    fi
    popd > /dev/null 2>&1
}


# @stdout ... the default config name
# @return ... $?
function get_default_config_name()
{
    #local config_names=($(get_config_names))
    #echo ${config_names[0]}
    echo "default"
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
        "DEVICE_HINT_STRING"
        "ALL_DEVICE_IDS"
        "PAD_DEVICE_IDS"
        "STYLUS_DEVICE_IDS"
        "ERASER_DEVICE_IDS"
        "CURSOR_DEVICE_IDS"
        "TOUCH_DEVICE_IDS"
        "XBINDKEYS_CFG"
    )
    local config_arrays=(
        "ALL_PARAMETERS"
        "PAD_PARAMETERS"
        "PAD_BUTTON_MAPPINGS"
        "STYLUS_PARAMETERS"
        "STYLUS_BUTTON_MAPPINGS"
        "ERASER_PARAMETERS"
        "ERASER_BUTTON_MAPPINGS"
        "CURSOR_PARAMETERS"
        "CURSOR_BUTTON_MAPPINGS"
        "TOUCH_PARAMETERS"
        "TOUCH_BUTTON_MAPPINGS"
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


# @stdout   ... next geometry
# @input $1 ... array of known geometries
# @input $2 ... current geometry (empty or unknown string falls back to 1st geometry)
# @return   ... $0
function get_next_geometry()
{
    local geometries=( $(echo "$1") )
    local geo=( $(echo "$1") )
    local current_geometry="$2"

    # if geometry not found: fallback to first
    
    if [[ ! " ${geometries[@]} " =~ " ${current_geometry} " ]] ; then
        echo "${geometries[0]}"
        return 0
    fi

    # if geometry found: take next
    geometries=( $(echo "${geometries[*]}" ) $(echo "${geometries[*]}" ))
    for i in "${!geometries[@]}" ; do
        if [ "x${geometries[$i]}" == "x$current_geometry" ] ; then
            let i=$i+1
            echo "${geometries[$i]}"
            return 0
        fi
    done

    return 1
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
function _get_device_id()
{
    grep --perl-regex --only-matching "(?<=id: )\s*[0-9]*\s*(?=type:)" | tr "\n" " " | tr -d "\t\r" | xargs
}

# @stdout ... all device numbers, space separated
# @input  ... none
# @return ... $?
function get_all_device_ids()
{
    xsetwacom --list devices | _get_device_id
}

# @stdout ... all device numbers, space separated
# @input  ... $1 optional case insensitive device hint i.e. "Wacom intuos Pro" or "Wacom Untuos BT"
# @return ... $?
function get_device_ids()
{
    local device_hint="$1"
    xsetwacom --list devices | grep -i "$device_hint" | _get_device_id

}

# @stdout ... pad device numbers, space separated
# @input  ... $1 optional device hint
# @return ... $?
function get_pad_device_ids()
{
    local device_hint="$1"
    xsetwacom --list devices | grep -i "$device_hint" | grep "pad" | _get_device_id
}


# @stdout ... stylus device numbers, space separated
# @input  ... $1 optional device hint
# @return ... $?
function get_stylus_device_ids()
{
    local device_hint="$1"
    xsetwacom --list devices | grep -i "$device_hint" | grep "stylus" | _get_device_id
}


# @stdout ... eraser device numbers, space separated
# @input  ... $1 optional device hint
# @return ... $?
function get_eraser_device_ids()
{
    local device_hint="$1"
    xsetwacom --list devices | grep -i "$device_hint" | grep "eraser" | _get_device_id
}

# @stdout ... cursor device numbers, space separated
# @input  ... $1 optional device hint
# @return ... $?
function get_cursor_device_ids()
{
    local device_hint="$1"
    xsetwacom --list devices | grep -i "$device_hint" | grep "cursor" | _get_device_id
}

# @stdout ... eraser device numbers, space separated
# @input  ... $1 optional device hint
# @return ... $?
function get_touch_device_ids()
{
    local device_hint="$1"
    xsetwacom --list devices | grep -i "$device_hint" | grep "touch" | _get_device_id
}

# @input $1 ... identation
# @stdout   ... all supported device parameters
# @return   ... $?
function print_all_device_parameters()
{
    local identation=$1
    for device_id in $(get_device_ids "$DEVICE_HINT_STRING") ; do
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
# @stdout ... diff of XSETWACOM_PARAMS_OLD and print_all_device_parameters
# @return ... $?
function print_effective_changes()
{
    local xsewacom_params_new=$(print_all_device_parameters)
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
            pushd "$SCRIPT_PATH" > /dev/null 2>&1
            echo "bind keys with $SCRIPT_PATH/configs/$XBINDKEYS_CFG_FILE (running in background)"
            xbindkeys --file "$SCRIPT_PATH/configs/$XBINDKEYS_CFG_FILE" > /dev/null 2>&1
            popd
        ;;
        nodaemon)
            pushd "$SCRIPT_PATH" > /dev/null 2>&1
            echo "bind keys with $SCRIPT_PATH/configs/$XBINDKEYS_CFG_FILE"
            xbindkeys --file "$SCRIPT_PATH/configs/$XBINDKEYS_CFG_FILE" --verbose --nodaemon
            popd
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


# ============================ section plot ============================


# @pre      ... cofiguration is loaded
# @input    ... nothing
# @stdout   ... control points
# @exit     ... no exit
# @return   ... $?
# @requires ... gnuplot
function plot_pressure_curve()
{
    local array_name=$1
    declare -n aarray=$1
        
    declare -a pc
    pc=(${aarray[PressureCurve]})
    local plot_data="0 0\n${pc[0]} ${pc[1]}\n${pc[2]} ${pc[3]}\n100 100\n"

    echo -e "bezier pressure curve control points:\nx y"
    echo -e "$plot_data"
    
    echo -e "${plot_data}e\n" | tee -a /dev/stdout \
    | gnuplot -p -e "set grid; plot '-' using 1:2 smooth bezier title 'pressure curve', '' using 1:2 with linespoints pointtype 3 title 'control points'"
}

# Live plots the current pressure mapped from 0 to 65536.
# @pre      ... nothing
# @input $1 ... optional device hint/name, e.g. "pen stylus" or "pen eraser"
# @stdout   ... nothing
# @exit     ... no exit
# @return   ... $?
# @requires ... xinput, feedgnuplot
function plot_current_pressure()
{
    local device_hint="pen stylus"

    if [ -n "$1" ] ; then
      device_hint="$1"
    fi

    device_info=`xinput --list | grep -i "$device_hint"`
    declare -a device_ids
    device_ids=(`echo "$device_info" | grep -i "$device_hint" | grep --perl-regexp --only-matching "(?<=id=).*(?=\[)" | tr --delete "[:blank:]"`)
    device_id=${device_ids[0]}

    if [ -z "$device_id" ] ; then
      echo "no device found with hint \"$device_hint\""
      return
    else
      echo -e "found device(s):\n$device_info"
      echo "chosen id: $device_id"
    fi

    xinput --test "$device_id" \
      | awk -F '[[:blank:]]*a\\[[[:digit:]]+\\]=' '{ if ($4 > 0) {print $4 ; fflush()} }' \
      | feedgnuplot --exit --stream 0.25 --y2 1 --lines --unset grid --xlen 1000 --ymin 0 --ymax 65536 --y2min 0 --y2max 65536
}
