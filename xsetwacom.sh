#!/bin/env bash

SCRIPT_NAME="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
SCRIPT_PATH="$(dirname "$(test -L "$0" && readlink "$0" || echo "$0")")"

source ${SCRIPT_PATH}/src/utils.sh

GEOMETRIES=($(get_geometries))
SELECTED_GEOMETRY=${GEOMETRIES[0]}
POINTER_MODE="Absolute"
PRESSURE_CURVE="0 0 50 70"
CONFIG_NAME=$(get_default_config_name)
XSETWACOM_OLD_CFG=$(print_all_devices_parameters)


# @input  ... none
# @return ... $?
function usage()
{
    local config_names=$(get_config_names | tr " " "|")    
    echo -en "\nUsage: $SCRIPT_NAME [OPTION ...] \n"
    echo -en "\n"
    echo -en " Options:\n"
    echo -en "  --help              Print this help.\n"
    echo -en "  --map [primary|seconary|whole]\n"
    echo -en "                      Map to primary secondary or all monitor(s) (as reported by xrandr).\n"
    echo -en "                      Current geometries are:\n"
    echo -en "                        primary   = ${GEOMETRIES[1]}\n"
    echo -en "                        secondary = ${GEOMETRIES[2]}\n"
    echo -en "                        whole     = ${GEOMETRIES[0]}\n"
    echo -en "                      Default: $SELECTED_GEOMETRY\n"
    echo -en "  --mode              Absolute or Relative behaviour.\n"
    echo -en "                      Default: Absolute\n"
    echo -en "  --curve [x1 y1 x2 y2]\n"
    echo -en "                      Set the pressure curve (3rd oder Bezier)\n"
    echo -en "                      Default: ${ALL_PARAMETERS[PressureCurve]}\n"
    echo -en "  --config [${config_names}]\n"
    echo -en "                      Create your own configs in ./configs/.\n"
    echo -en "                      Default: ${CONFIG_NAME}.\n"
    echo -en "  --parameters        Print all device parameters and exit.\n"
    echo -en "\n\n"
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
                POINTER_MODE=$2
                shift
                shift
            ;;
            --curve)
                shift
                if [ "x" != "x$1" ] ; then
                    PRESSURE_CURVE=$1
                    shift
                fi
            ;;
            --config)
                shift
                if [ "x" != "x$1" ] ; then
                    CONFIG_NAME=$1
                    shift
                fi
            ;;
            --parameters)
                print_all_devices_parameters
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
    echo "${identation}Configure device $device_id with $config_mapping_name"
    # TODO
    
    for config_mapping_postfix in ${config_mappings[@]} ; do
        config_mapping_name=$config_mappoing_prefix$config_mapping_postfix
        echo "${identation}Configure device $device_id with $config_mapping_name"
        # TODO
    done
}


# @stdout   ... logging
# @input $1 ... device id
# @exit 1   ... on error
# @return   ... $?
function main() 
{
    # TODO: post_config: collect all vars for simpler pritn_loaded_config impl
    # TODO: implement handling of: xbindkeys --file default-xbindkeys.dfg
    
    local identation="  "
    parse_cli_args "$@" \
    && exit_if_no_device_found && echo "Found devices:" && print_devices "$identation" \
    && load_config "$CONFIG_NAME" \
    && echo "Configuration \"$CONFIG_NAME\" loaded:" && print_loaded_config "  " \
    && echo "Configure devices:" && configure_devices "$identation" \
    && echo "Current device settings:" && print_all_devices_parameters "$identation" \
    && echo "Device settings diff (old vs. new config):" \
    && echo $(diff <(echo "$XSETWACOM_OLD_CFG") <(print_all_devices_parameters) && echo "xsetwacom reported no changes" ) | awk '{ print "  " $0 }'
}

main $@
