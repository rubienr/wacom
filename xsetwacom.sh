#!/bin/env bash
SCRIPT_NAME="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
SCRIPT_PATH="$(dirname "$(test -L "$0" && readlink "$0" || echo "$0")")"

source ${SCRIPT_PATH}/src/utils.sh
XSETWACOM_PARAMS_OLD=$(print_all_devices_parameters)

# default arguments until the config is loaded
GEOMETRIES=($(get_geometries))
SELECTED_GEOMETRY=${GEOMETRIES[0]}
CONFIG_NAME=$(get_default_config_name)

# @input  ... none
# @return ... $?
function usage()
{
    local config_names=$(get_config_names | tr " " "|")
    echo -en "Usage: $SCRIPT_NAME [OPTION ...] \n"
    echo -en "\n"
    echo -en "Without command line arguments the script loads the default conguration and applies the parameters to attached device(s).\n"
    echo -en "\n"
    echo -en "Options:\n"
    echo -en "\n"
    echo -en "  --parameters        Print all supported device parameters and exit.\n"
    echo -en "  --print-config [${config_names}]\n"
    echo -en "                      Print the configuration and exit.\n"
    echo -en "                      Default: ${CONFIG_NAME}.\n"
    echo -en "  --help              Print this help.\n"
    echo -en "\n"
    echo -en "  A few device arguments can be defined by command line. Any other must be defined in the configuration file.\n"
    echo -en "\n"
    echo -en "  --config [${config_names}]\n"
    echo -en "                      If specified always let this argument be the 1st on command line. Create your own configs in ./configs/.\n"
    echo -en "                      Default: ${CONFIG_NAME}.\n"
    echo -en "  --map [primary|seconary|whole]\n"
    echo -en "                      Map device to primary, secondary or all monitor(s) (as reported by xrandr).\n"
    echo -en "                      Reported geometries are:\n"
    echo -en "                        primary   = ${GEOMETRIES[1]}\n"
    echo -en "                        secondary = ${GEOMETRIES[2]}\n"
    echo -en "                        whole     = ${GEOMETRIES[0]}\n"
    echo -en "                      Default: $SELECTED_GEOMETRY\n"
    echo -en "  --mode [Absolute|Relative]\n"
    echo -en "                      Absolute or relative pointer behaviour.\n"
    echo -en "                      Default: ${ALL_PARAMETERS[Mode]}\n"
    echo -en "  --curve [x1 y1 x2 y2]\n"
    echo -en "                      Set the pressure curve (3rd oder Bezier)\n"
    echo -en "                      Default: ${ALL_PARAMETERS[PressureCurve]}\n"
    echo -en "\n"
    echo -en "  Key binding manipulaton (see allso xbindkeys manual).\n"
    echo -en "\n"
    echo -en "  --xbindkeys [nodaemon|daemon|reload|kill]\n"
    echo -en "                      Manipulate system key bindings and exit.\n"
    echo -en "                        nodaemon: start xbindkeys with configuration ${XBINDKEYS_CFG_FILE} in foreground\n"
    echo -en "                        daemon:   start xbindkeys with configuration ${XBINDKEYS_CFG_FILE} in background\n"
    echo -en "                        reload:   tell xbindkeys to reaload the configuration\n"
    echo -en "                        kill:     try to stop all xbindkeys instances\n"
    echo -en "                      Default: ${XBINDKEYS_MODE}.\n"
}


# @input  ... "$@"
# @return ... $?
function parse_cli_args()
{
    local whole_geometry=${GEOMETRIES[0]}
    local primary_geometry=${GEOMETRIES[1]}
    local secondary_geometry=${GEOMETRIES[2]}
    SELECTED_GEOMETRY=$primary_geometry
        
    while [[ $# -gt 0 ]] ; do
        local key="$1"

        case $key in
            -h|--help)
                try_load_config "$CONFIG_NAME"
                usage
                exit 0
            ;;
            --map)
                shift
                if [ "xprimary" == "x$1" ] ; then
                    SELECTED_GEOMETRY=$primary_geometry
                elif [ "xsecondary" == "x$1" ] ; then
                    SELECTED_GEOMETRY=$secondary_geometry
                elif [ "xwhole" == "x$1" ] ; then
                    SELECTED_GEOMETRY=$whole_geometry
                else
                    usage
                    exit 1
                fi
                shift
            ;;
            --mode)
                ALL_PARAMETERS+=([Mode]="$2")
                shift
                shift
            ;;
            --curve)
                shift
                if [ "x" != "x$1" ] ; then
                    PRESSURE_CURVE="$1"
                    shift
                fi
            ;;
            --config)
                shift
                if [ "x" != "x$1" ] ; then
                    CONFIG_NAME="$1"
                    shift
                fi
            ;;
            --parameters)
                print_all_devices_parameters
                exit 0
            ;;
            --print-config)
                shift
                if [ "x" != "x$1" ] ; then
                    CONFIG_NAME="$1"
                    shift
                fi
                try_load_config "$CONFIG_NAME"
                print_loaded_config
                exit 0
            ;;
            --xbindkeys)
                shift
                load_config "$CONFIG_NAME"
                if [ "xnodaemon" == "x$1" -o  \
                     "xdaemon" == "x$1" -o \
                     "xreload" == "x$1" -o \
                     "xkill" == "x$1" -o \
                     "xreload" == "x$1" ] ; then
                    XBINDKEYS_MODE=$1
                    shift
                fi
                bind_keys "$XBINDKEYS_MODE"
                exit 0
            ;;
            *)
                try_load_config "$CONFIG_NAME"
                usage
                exit 1
            ;;
        esac
    done
    return 0
}


# @input $1 ... identation
# @pre      ... config loaded
# @stdout   ... logging
# @return   ... $?
function configure_devices()
{
    local identation=$1
    local connected_device_ids=$(get_all_device_ids)

    for device_id in $PAD_DEVICE_IDS ; do
        echo "${identation}Configure pad device $device_id"
        echo $connected_device_ids | grep $device_id > /dev/null 2>&1 \
        && configure_device $device_id "PAD" "${identation}${identation}" \
        || echo "${identation}Pad device $device_id not connected. Configuration skipped for $device_id."
    done

    for device_id in $STYLUS_DEVICE_IDS ; do
        echo "${identation}Configure pen device $device_id"
        echo $connected_device_ids | grep $device_id > /dev/null 2>&1 \
        && configure_device $device_id "STYLUS" "${identation}${identation}" \
        || echo "${identation}Stylus device $device_id not connected. Configuration skipped for $device_id."
    done

    for device_id in $ERASER_DEVICE_IDS ; do
        echo "${identation}Configure eraser device $device_id"
        echo $connected_device_ids | grep $device_id > /dev/null 2>&1\
        && configure_device $device_id "ERASER" "${identation}${identation}" \
        || echo "${identation}Eraser device $device_id not connected. Configuration skipped for $device_id."
    done
}

# @pre      ... config loaded
# @stdout   ... logging
# @input $1 ... device id
# @input $2 ... device config prefix (PEN, BUTTON, ERASER)
# @input $3 ... identation
# @return   ... $?
function configure_device()
{
    local device_id=$1
    local config_mappoing_prefix=$2
    local identation=$3
    local config_mappings=(
        _PARAMETERS
        _BUTTON_MAPPING
    )
    local config_mapping_name=""
    
    config_mapping_name="ALL_PARAMETERS"
    echo "${identation}Configure device $device_id with $config_mapping_name (${#ALL_PARAMETERS[@]})"
    set_device_parameters "$device_id" "ALL_PARAMETERS" "$identation$identation"

    for config_mapping_postfix in ${config_mappings[@]} ; do
        config_mapping_name=$config_mappoing_prefix$config_mapping_postfix
        declare -n ref=$config_mapping_name
        echo "${identation}Configure device $device_id with $config_mapping_name (${#ref[@]})"
        unset -n ref
        set_device_parameters "$device_id" "$config_mapping_name" "$identation$identation"
    done
}


# @stdout   ... logging
# @input $1 ... device id
# @exit 1   ... on error
# @return   ... $?
function main() 
{
    local identation="  "
    parse_cli_args "$@" \
    && exit_if_no_device_found && echo "Found devices:" && print_devices "$identation" \
    && load_config "$CONFIG_NAME" \
    && echo "Configuration \"$CONFIG_NAME\" loaded:" && print_loaded_config "  " \
    && echo "Configure devices: $(get_all_device_ids)" && configure_devices "$identation" \
    && echo "Current device settings:" && print_all_devices_parameters "$identation" \
    && echo "Device settings diff (old vs. new config):" && print_effective_changes
}

main $@
