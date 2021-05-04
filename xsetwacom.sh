#!/bin/bash
SCRIPT_NAME="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
#
# Simple wacom setup: maps to primary screen
#

#
# section init
#
declare -A parameters
declare -A pad_button_mapping

PRIMARY_GEOMETRY=$(xrandr -q | grep --perl-regex --only-matching "(?<= connected primary )\s*[0-9x+]*")
SECONDARY_GEOMETRY=$(xrandr -q | grep --perl-regex --only-matching "(?<= connected )\s*[0-9x+]*")
WHOLE_GEOMETRY=$(xrandr -q | grep --perl-regex --only-matching "(?<= current )\s*[0-9x ]*\s*(?=, maximum )" | tr -d "\r\n " && echo -n "+0+0")
DEVICE_IDS=$(xsetwacom --list devices | grep --perl-regex --only-matching "(?<=id: )\s*[0-9]*\s*(?=type:)" | tr "\n" " " | tr -d "\t\r")

#
# section default values
#


parameters["MapToOutput"]=$PRIMARY_GEOMETRY
parameters["Mode"]="Absolute"
parameters["PressureCurve"]="0 0 50 70"

# TODO rubienr - refactor that implementation
declare -A pad_button_mapping_default
pad_button_mapping_default["Button 1"]="11"
pad_button_mapping_default["Button 2"]="12"
pad_button_mapping_default["Button 3"]="13"
pad_button_mapping_default["Button 8"]="14"

declare -A pad_button_mapping_krita
pad_button_mapping_krita["Button 1"]="key +b -b"
pad_button_mapping_krita["Button 2"]="key +x -x"
pad_button_mapping_krita["Button 3"]="key +altgr 8 key +altgr 8 key +altgr 8"
pad_button_mapping_krita["Button 8"]="key +altgr 9 key +altgr 9 key +altgr 9"

declare -A pad_button_mapping_gimp
pad_button_mapping_gimp["Button 1"]="key p"
pad_button_mapping_gimp["Button 2"]="key +x -x"
pad_button_mapping_gimp["Button 3"]=""
pad_button_mapping_gimp["Button 8"]=""

declare -A pad_button_mapping
for i in "${!pad_button_mapping_default[@]}" ; do
    pad_button_mapping[$i]=${pad_button_mapping_default[$i]}
done
# TODO rubienr - refactor that implementation - end

#
# @params - none
# @return - $?
#
function usage()
{
    echo -en "\nUsage: $SCRIPT_NAME [OPTION ...] \n"
    echo -en "\n"
    echo -en " Options:\n"
    echo -en "  -h, --help          Print this help.\n"
    echo -en "  -m, --map [[p|primary] | [s|seconary] | [a|all]]\n"
    echo -en "                      Map to primary secondary or all monitor(s) (as reported by xrandr).\n"
    echo -en "                      Default: primary ($PRIMARY_GEOMETRY)\n"
    echo -en "  -o, --mode          Absolute or Relative behaviour. Default: Absolute\n"
    echo -en "  -c, --curve [x1 y1 x2 y2]\n"
    echo -en "                      Set the pressure curve (3rd oder Bezier)\n"
    echo -en "                      Default: ${parameters[PressureCurve]}\n"
    echo -en "  -b, --buttons [default | krita | gimp]\n"
    echo -en "                      Idividual button mapping.\n"
    echo -en "                      Default: default.\n"
    echo -en "  -p, --parameters    Print all device parameters.\n"
    echo -en "\n\n"
}

#
# @params - "$@"
# @return - $?
#
function parse_cli_args()
{
    while [[ $# -gt 0 ]]
    do
    key="$1"

    case $key in
        -h|--help)
            usage
            exit 0
        ;;
        -m|--map)
            shift
            if [ "xp" == "x$1" -o "xprimary" == "x$1" ] ; then
                parameters["MapToOutput"]=$PRIMARY_GEOMETRY
            elif [ "xs" == "x$1" -o "xsecondary" == "x$1" ] ; then
                parameters["MapToOutput"]=$SECONDARY_GEOMETRY
            elif [ "xa" == "x$1" -o "xall" == "x$1" ] ; then
                parameters["MapToOutput"]=$WHOLE_GEOMETRY
            else
                usage
                exit 1
            fi
            shift
        ;;
        -o|--mode)
            parameters["Mode"]=$2
            shift
            shift
        ;;
        -c|--curve)
            shift
            if [ "x" != "x$1" ] ; then
                parameters["PressureCurve"]=$1
                shift
            fi
        ;;
        -b|--buttons)
            shift
            
            if [ "xdefault" == "x$1" ] ; then
                for i in "${!pad_button_mapping_default[@]}" ; do
                    pad_button_mapping[$i]=${pad_button_mapping_default[$i]}
                done
            elif [ "xkrita" == "x$1" ] ; then
                for i in "${!pad_button_mapping_krita[@]}" ; do
                    pad_button_mapping[$i]=${pad_button_mapping_krita[$i]}
                done
            elif [ "xgimp" == "x$1" ] ; then
                for i in "${!pad_button_mapping_gimp[@]}" ; do
                    pad_button_mapping[$i]=${pad_button_mapping_gimp[$i]}
                done
            else
                usage
                exit 1
            fi

            
            shift
        ;;
        -p|--parameters)
            print_parameters
            exit 0
        ;;
        *)
            usage
            exit 1
        ;;
    esac
    done
}

#
# section impl
#

#
# @params - none
# @return - $?
#
function print_config()
{
    echo -en "\nCurrent configuration:\n"
    for parameter in "${!parameters[@]}"
    do
      value=${parameters[$parameter]}
      echo -en "\t$parameter:\n\t\t$value\n"
    done

    echo -en "\n\tPad buttons:\n"
    for button in "${!pad_button_mapping[@]}" ; do
        local value=${pad_button_mapping[$button]}
        echo -en "\t\t$button -> \"$value\"\n"
    done
}

#
# @params - none
# @return - $?
#
function print_parameters()
{
    echo -en "\nCurrent device settings:\n"
    for device in $DEVICE_IDS
    do
        echo -en "\nDevice $device parameters:\n"
        xsetwacom --shell --get $device all 2>&1 | grep -v "does not exist"
    done
}

#
# TODO rubienr - refactor that implementation
# 
function set_button_mapping()
{
    local device=11 # todo
    echo -en "\t- device $device\n"
    for button in "${!pad_button_mapping[@]}" ; do
        local value=${pad_button_mapping[$button]}
        echo -en "\t\t$button -> \"$value\"\n"
        xsetwacom --set $device $button $value 2>&1 | awk '{ print "\t\t\t" $0 }'
    done
}

#
# @params - none
# @return - $?
#
function set_parameters()
{
    echo -en "\nSet parameters:\n"
    for device in $DEVICE_IDS
    do
        echo -e "\t- device $device"
        for parameter in "${!parameters[@]}"
        do
            #echo -e "\t\t- device &device"
            value=${parameters[$parameter]}
            echo -e "\t\t$parameter '$value'"
            xsetwacom --set $device $parameter $value 2>&1 | awk '{ print "\t\t\t" $0 }'
        done
    done
    set_button_mapping
}

#
# @params - none
# @return - $?
#
function main() 
{
    parse_cli_args "$@"
    print_config

    if [ "x" == "x$DEVICE_IDS" ] ; then
        echo -en "\nNo device found!\n"
        exit 1
    fi

    set_parameters
    print_parameters
}

main $@
