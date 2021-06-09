#!/bin/env bash
#set -x
SCRIPT_NAME="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
SCRIPT_PATH="$(dirname "$(test -L "$0" && readlink "$0" || echo "$0")")"

source ${SCRIPT_PATH}/src/utils.sh
XSETWACOM_PARAMS_OLD=""
GEOMETRIES=($(get_geometries))
CONFIG_NAME=$(get_default_config_name)

load_base_config

# @input  ... none
# @return ... $?
function usage()
{
    echo -en "Usage: $SCRIPT_NAME [OPTION ...] \n"
    echo -en "\n"
    echo -en "Without command line arguments the script loads the default conguration and applies the parameters to attached device(s).\n"
    echo -en "Note: always specify --config as first prameter (even for --help).\n"
    echo -en "\n"
    echo -en "Options:\n"
    echo -en "\n"
    echo -en "  --parameters        Print all supported device parameters and exit.\n"
    echo -en "  --configs           List all configuration names and exit.\n"
    echo -en "  --print-config [<config-name>]\n"
    echo -en "                      Print the configuration and exit.\n"
    echo -en "                      config-name: see --configs.\n"
    echo -en "                      Default: ${CONFIG_NAME}.\n"
    echo -en "  --help              Print this help.\n"
    echo -en "\n"
    echo -en "  A few device arguments can be defined by command line. Any other must be defined in the configuration file.\n"
    echo -en "\n"
    echo -en "  --config [<config-name>]\n"
    echo -en "                      If specified always let this argument be the 1st on command line. Create your own configs in ./configs/.\n"
    echo -en "                      config-name: see --configs.\n"
    echo -en "                      Default: ${CONFIG_NAME}.\n"
    echo -en "  --map [primary|seconary|whole|next]\n"
    echo -en "                      Map device to primary, secondary or all monitor(s) (as reported by xrandr).\n"
    echo -en "                      xrandr reported geometries are:\n"
    echo -en "                        primary   = ${GEOMETRIES[1]}\n"
    echo -en "                        secondary = ${GEOMETRIES[2]}\n"
    echo -en "                        whole     = ${GEOMETRIES[0]}\n"
    echo -en "                        next      = next geometry (cycles through all geometries)\n"
    echo -en "                      Default: ${ALL_PARAMETERS[MapToOutput]}\n"
    echo -en "  --mode [Absolute|Relative]\n"
    echo -en "                      Absolute or relative pointer behaviour.\n"
    echo -en "                      Default: ${ALL_PARAMETERS[Mode]}\n"
    echo -en "\n"
    echo -en "  Key binding manipulaton (see also xbindkeys manual).\n"
    echo -en "\n"
    echo -en "  --xbindkeys [nodaemon|daemon|reload|kill]\n"
    echo -en "                      Manipulate system key bindings and exit.\n"
    echo -en "                        nodaemon: start xbindkeys with configuration ${XBINDKEYS_CFG_FILE} in foreground\n"
    echo -en "                        daemon:   start xbindkeys with configuration ${XBINDKEYS_CFG_FILE} in background\n"
    echo -en "                        reload:   tell xbindkeys to reaload the configuration\n"
    echo -en "                        kill:     try to stop all xbindkeys instances\n"
    echo -en "                      Default: ${XBINDKEYS_MODE}.\n"
    echo -en "\n"
    echo -en "  Plot pressure cure.\n"
    echo -en "\n"
    echo -en "  --curve\n"
    echo -en "                      Plot the configured pressure curve and the resulting Bezier curve.\n"
    echo -en "  --pressure\n"
    echo -en "                      Live plot the current pressure curve. The pressure plot does not appear until the first pressure value is reported.
}\n"
}


# @input  ... "$@"
# @return ... $?
function parse_cli_args()
{
    local is_config_loaded="false"
    while [[ $# -gt 0 ]] ; do
        local key="$1"

        case $key in
            -h|--help)
                load_config "$CONFIG_NAME"
                usage
                exit 0
            ;;
            --map)
                shift
                if [ "xprimary" == "x$1" ] ; then
                    ALL_PARAMETERS[MapToOutput]=${GEOMETRIES[1]}
                elif [ "xsecondary" == "x$1" ] ; then
                    ALL_PARAMETERS[MapToOutput]=${GEOMETRIES[2]}
                elif [ "xwhole" == "x$1" ] ; then
                    ALL_PARAMETERS[MapToOutput]=${GEOMETRIES[0]}
                elif [ "xnext" == "x$1" ] ; then
                    ALL_PARAMETERS[MapToOutput]="next"
                else
                    usage
                    exit 1
                fi
                shift
            ;;
            --mode)
                shift
                if [ "xAbsolute" == "x$1" -o "xRelative" == "x$1" ] ; then
                    ALL_PARAMETERS+=([Mode]="$1")
                else
                    echo "Invalid --mode \"$1\"."
                    exit 1
                fi
                shift
            ;;
            --configs)
                echo "Configurations found:"
                for c in `get_config_names` ; do
                  echo "  $c"
                done
                exit 0
            ;;
            --config)
                shift
                if [ "x" != "x$1" ] ; then
                    CONFIG_NAME="$1"
                    is_config_loaded="true"
                    shift
                fi
                load_config "$CONFIG_NAME"
            ;;
            --parameters)
                print_all_device_parameters
                exit 0
            ;;
            --print-config)
                shift
                if [ "x" != "x$1" ] ; then
                    CONFIG_NAME="$1"
                    shift
                fi

                if [ "xfalse" == "x$is_config_loaded" ] ; then
                    load_config "$CONFIG_NAME"
                fi
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
            --curve)
                shift
                # todo - ERASER_PARAMETERS
                plot_pressure_curve "STYLUS_PARAMETERS"
                exit 0
            ;;
            --pressure)
                shift
                # todo - "Pen eraser"
                plot_current_pressure "Pen stylus"
                exit 0
            ;;
            *)
                if [ "xfalse" == "x$is_config_loaded" ] ; then
                    load_config "$CONFIG_NAME"
                fi
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
    local connected_device_ids=$(get_device_ids "$DEVICE_HINT_STRING")

    for device_id in $PAD_DEVICE_IDS ; do
        test -n "$device_id" \
        && echo "$connected_device_ids" | grep "$device_id" > /dev/null 2>&1 \
        && echo "${identation}Configure pad device $device_id" \
        && configure_device $device_id "PAD" "${identation}${identation}" \
        || echo "${identation}Pad device $device_id not connected. Configuration skipped for $device_id."
    done

    for device_id in $STYLUS_DEVICE_IDS ; do
        test -n "$device_id" \
        && echo "$connected_device_ids" | grep "$device_id" > /dev/null 2>&1 \
        && echo "${identation}Configure pen device $device_id" \
        && configure_device $device_id "STYLUS" "${identation}${identation}" \
        || echo "${identation}Stylus device $device_id not connected. Configuration skipped for $device_id."
    done

    for device_id in $ERASER_DEVICE_IDS ; do
        test -n "$device_id" \
        && echo "$connected_device_ids" | grep "$device_id" > /dev/null 2>&1 \
        && echo "${identation}Configure eraser device $device_id" \
        && configure_device $device_id "ERASER" "${identation}${identation}" \
        || echo "${identation}Eraser device $device_id not connected. Configuration skipped for $device_id."
    done

    for device_id in $CURSOR_DEVICE_IDS ; do
        test -n "$device_id" \
        && echo "$connected_device_ids" | grep "$device_id" > /dev/null 2>&1 \
        && echo "${identation}Configure cursor device $device_id" \
        && configure_device $device_id "CURSOR" "${identation}${identation}" \
        || echo "${identation}Cursor device $device_id not connected. Configuration skipped for $device_id."
    done

    for device_id in $TOUCH_DEVICE_IDS ; do
        test -n "$device_id" \
        && echo "$connected_device_ids" | grep "$device_id" > /dev/null 2>&1\
        && echo "${identation}Configure touch device $device_id" \
        && configure_device $device_id "TOUCH" "${identation}${identation}" \
        || echo "${identation}Touch device $device_id not connected. Configuration skipped for $device_id."
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
        _BUTTON_MAPPINGS
    )
    local config_mapping_name=""
    
    config_mapping_name="ALL_PARAMETERS"
    echo "${identation}Configure device $device_id with ${#ALL_PARAMETERS[@]} $config_mapping_name"
    set_device_parameters "$device_id" "ALL_PARAMETERS" "$identation$identation"

    for config_mapping_postfix in ${config_mappings[@]} ; do
        config_mapping_name=$config_mappoing_prefix$config_mapping_postfix
        declare -n ref=$config_mapping_name
        echo "${identation}Configure device $device_id with ${#ref[@]} $config_mapping_name"
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
    pushd "$SCRIPT_PATH" > /dev/null 2>&1
    parse_cli_args "$@" \
    && exit_if_no_device_found && warn_if_device_in_android_mode \
    && echo "Found devices:" && print_devices "$identation" \
    && load_config "$CONFIG_NAME" \
    && XSETWACOM_PARAMS_OLD=$(print_all_device_parameters) \
    && echo "Configuration \"$CONFIG_NAME\" loaded:" && print_loaded_config "  " \
    && echo "Configure ${#ALL_DEVICE_IDS[@]} devices of $DEVICE_HINT_STRING (${ALL_DEVICE_IDS[@]}):" && configure_devices "$identation" \
    && echo "Current device settings:" && print_all_device_parameters "$identation" \
    && echo "Device settings diff (old vs. new config):" && print_effective_changes
    popd > /dev/null 2>&1
}

main $@
