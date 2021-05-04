#!/bin/bash
SCRIPT_NAME="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
#
# Simple wacom setup: maps to primary screen
#

#
# section init
#
declare -A parameters
PRIMARY_GEOMETRY=$(xrandr -q | grep --perl-regex --only-matching "(?<= connected primary )\s*[0-9x+]*")
SECONDARY_GEOMETRY=$(xrandr -q | grep --perl-regex --only-matching "(?<= connected )\s*[0-9x+]*")
WHOLE_GEOMETRY=$(xrandr -q | grep --perl-regex --only-matching "(?<= current )\s*[0-9x ]*\s*(?=, maximum )" | tr -d " ")
DEVICE_IDS=$(xsetwacom --list devices | grep --perl-regex --only-matching "(?<=id: )\s*[0-9]*\s*(?=type:)" | tr "\n" " " | tr -d "\t\r")

#
# section default values
#

parameters["MapToOutput"]=$PRIMARY_GEOMETRY
parameters["Mode"]="Absolute"
parameters["PressureCurve"]="0 0 50 70"

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
	echo -en "  -m, --map [p|primary|s|seconary|a|all]\n"
    echo -en "                      Map to primary secondary or all monitor(s) (as reported by xrandr).\n"
    echo -en "                      Default: primary ($PRIMARY_GEOMETRY)\n"
	echo -en "  -o, --mode          Absolute or Relative behaviour. Default: Absolute\n"
	echo -en "  -c, --curve [x1 y1 x2 y2]\n"
    echo -en "                      Set the pressure curve (3rd oder Bezier)\n"
    echo -en "                      Default: ${parameters[PressureCurve]}\n"
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
		-m|--map) # p ... primary, s ... secondary, a ... all
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
	echo -en "\nConfiguration:\n"
	for parameter in "${!parameters[@]}"
	do
	  value=${parameters[$parameter]}
	  echo -en "\t$parameter:\n\t\t$value\n"
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
		xsetwacom --get $device all 2>&1 | grep -v "does not exist"
	done
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
	# TODO - map buttons: 1 2 3 8
}

main $@
