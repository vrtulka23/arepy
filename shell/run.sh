#!/bin/bash
#set -e  # exit always if there is some error
 
DIR_PWD=$(pwd)                          # directory where we run the script
DIR_AREPY=$(dirname $(dirname $0))          # directory of the arepy module
DIR_RESULTS=$DIR_AREPY/results              # directory with scripy results
DIR_PYTHON_AREPY=$DIR_AREPY/python/arepy    # arepy python scripts
DIR_PYTHON_SCRIPY=$DIR_AREPY/python/scripy  # scripy python scripts

# Find out a project name and directory
PROJECT_NAME="none"
DIR_PROJECT="none"
nd=$(ls -l $DIR_PYTHON_SCRIPY | grep ^d | wc -l)  # count number of projects
if [ "$nd" -gt "0" ]; then
    for pdir in $(ls -d $DIR_PYTHON_SCRIPY/*)
    do
	pname=$(basename $pdir)
	if [ -f $pdir/__init__.py ]; then
	    psim=$(grep -o '".*"' $pdir/__init__.py | sed 's/"//g')
	    if [[ $DIR_PWD == "$psim"* ]]; then
		PROJECT_NAME="$pname"
		DIR_PROJECT="$pdir"
	    fi
	fi
    done
fi

# Load local settings
while [ "$DIR_PWD" != "/" ]
do
    if [ -e "$DIR_PWD/run.sh" ] # load settings from the current dir
    then
	source $DIR_PWD/run.sh
	break
    else                            # look in a parent directory
	DIR_PWD=$(dirname $DIR_PWD)
    fi
done

# Load system settings
source $DIR_AREPY/shell/system.sh

# Load default settings if necessary
DIR_HOME=${DIR_HOME:-$HOME}                    # home directory
DIR_AREPO=${DIR_AREPO:-"$DIR_AREPY/arepo"}     # directory with the arepo source code

NUM_NODES=${NUM_NODES:-1}                      # number of nodes
NUM_PROC=${NUM_PROC:-16}                       # number of processors per node
JOB_WALL_TIME=${JOB_WALL_TIME:-"1:00:00"}      # wall time of the run
JOB_TYPE=${JOB_TYPE:-"test"}                   # type of nodes
JOB_NAME=${JOB_NAME:-"test"}                   # job name

RUN_CMD_TERMINAL=${RUN_CMD_TERMINAL:-"mpirun -np $((NUM_NODES*NUM_PROC))"} # running command in terminal
RUN_CMD_SUBMIT=${RUN_CMD_SUBMIT:-"mpirun"}     # running command in submit script
SUBMIT_CMD=${SUBMIT_CMD:-"msub"}               # submit command
SUBMIT_INIT=${SUBMIT_INIT:-""}                 # initial submit settings
SUBMIT_END=${SUBMIT_END:-""}                   # end submit settings
SUBMIT_LOG=${SUBMIT_LOG:-"submit"}             # submit log file name prefix
CANCEL_CMD=${CANCEL_CMD:-"canceljob"}          # command to cancel a job
JOBID_REGEXP=${JOBID_REGEXP:-"[0-9]+"}         # regular expression that extracts the job id from the subit message
INTER_CMD=${INTER_CMD:-"echo 'INTER_CMD is not set'"}    # command that starts runs the interactive session

FLAGS_RUN=${FLAGS_RUN:-""}                     # arepo run flags
FLAGS_RESTART=${FLAGS_RESTART:-"1"}            # arepo restart flags
PARAM_FILE=${PARAM_FILE:-"param.txt"}          # arepo parameter file
CONFIG_FILE=${CONFIG_FILE:-"Config.sh"}        # arepo configuration file
CLEAN_FILES=${CLEAN_FILES:-""}                 # additional files to be cleaned

IMAGE_NODES=${IMAGE_NODES:-1}                    # number of nodes
IMAGE_PROC=${IMAGE_PROC:-16}                     # number of processors per node
IMAGE_WALLTIME=${IMAGE_WALLTIME:-"1:00:00"}      # wall time
IMAGE_TYPE=${IMAGE_TYPE:-"standard"}             # type of nodes
IMAGE_FLAGS=${IMAGE_FLAGS:-"(0 100 0 1 0 1 0 1"} # arepo image flags

# Local variables
CURRENT_TIME=$(date '+%s')                     # current date stemp
SIM_LOG=${SIM_LOG:-$DIR_AREPY/.submitlog}     # path to the file that logs the submit times

RED='\033[0;31m'                               # bash output mark for a red color
GRE='\033[0;32m'                               # bash output mark for a green color
YEL='\033[0;33m'                               # bash output mark for a yellow color
NC='\033[0m'                                   # bash output mark to terminate colors

# Helper functions
echo_green()
{
    echo -e "${GRE}$1${NC}"
}
echo_red()
{
    echo -e "${RED}$1${NC}"
}
submit_log_add()
{
    [ -f $2 ] && echo "$1" >> $2 || echo "$1" > $2
}
submit_log_get()
{
    grep "${1}:*" $2  | sed "s/$1: //"
}
output_num()
{
    nameOutput="output/output${1}*"
    ls -1 $nameOutput > /dev/null 2>&1
    if [ "$?" = "0" ]; then
	num=$(find $nameOutput | grep -Eo '[0-9]+' | sort -nr | head -n1)
	echo $(($num+1))
    else
	echo 0
    fi
}

# Functions to run a job in the terminal
terminal()
{
    eval="${RUN_CMD_TERMINAL} ./Arepo ${PARAM_FILE} ${2} | tee output/output_tr${1}.log"
    echo -e "${YEL}$eval${NC}"
    eval "$eval"
}
terminal_run()      # run simulations in the current environment
{
    echo_green "Runnig the simulation..."
    if [ $(type -t on_terminal_run) ]; then
	on_terminal_run
    fi
    terminal 0 "${FLAGS_RUN}"
}
terminal_restart()
{
    echo_green "Restarting the simulation..."
    if [ $(type -t on_terminal_restart) ]; then
	on_terminal_restart
    fi
    terminal $(output_num "_tr") "${FLAGS_RESTART}"
}
terminal_image()
{
    echo_green "Creating arepo image..."
    terminal "_img" "${FLAGS_IMAGE}"
}

# Functions used to submit a job to the queue
submit()
{
    if [ $1 = "IMG" ]; then
	submitInit=$(submit_init ${IMAGE_NODES} ${IMAGE_PROC} ${IMAGE_TYPE} ${IMAGE_WALLTIME} ${JOB_NAME})
    else
	submitInit=$(submit_init ${NUM_NODES} ${NUM_PROC} ${JOB_TYPE} ${JOB_WALL_TIME} ${JOB_NAME})
    fi
    submitLog="$SUBMIT_LOG${1}.log"
    echo "#!/bin/bash
${submitInit}
cd ${DIR_PWD}
printf \"Time-Start: %s\n\" \"\$(date '+%s')\" >> $submitLog
${2}
printf \"Time-End: %s\n\" \"\$(date '+%s')\" >> $submitLog
${SUBMIT_END}
" > "submit${1}.job"
    submitMsg=$(eval "${SUBMIT_CMD} submit${1}.job")
    echo $submitMsg
    jobID=$(echo $submitMsg | grep -Eo $JOBID_REGEXP) 
    submit_log_add "Job-ID: ${jobID}" "$submitLog"
    submit_log_add "Time-Submit: ${CURRENT_TIME}" "$submitLog"
    simName=${DIR_PWD#*$DIR_HOME}
    logmsg="$(date) - ${jobID} - ${simName}"
    [ -f $SIM_LOG ] &&	echo "$logmsg" >> $SIM_LOG || echo "$logmsg" > $SIM_LOG
}
submit_run()          # submit job to the cluster queue
{
    submitLog="${SUBMIT_LOG}0.log"
    if [ -f $submitLog ]; then
	while true; do
	    read -p $'\e[31mSubmitting a new job will delete all old data. Do you want to proceed? (y/N)\e[0m ' yn
	    case $yn in
		[Yy]* ) clean_directory; break;;
		[Nn]* ) exit;;
		* ) exit;;
	    esac
	done
    fi

    echo_green "Submitting the job..."
    if [ $(type -t on_submit_run) ]; then
	on_submit_run
    fi

    submit 0 "${RUN_CMD_SUBMIT} ./Arepo ${PARAM_FILE} ${FLAGS_RUN} > output/output0.log"
}
submit_restart()
{
    echo_green "Restarting the job..."
    if [ $(type -t on_submit_restart) ]; then
	on_submit_restart
    fi
    outputNum=$(output_num "")
    submit $outputNum "${RUN_CMD_SUBMIT} ./Arepo ${PARAM_FILE} ${FLAGS_RESTART} > output/output${outputNum}.log"
}
submit_image()
{
    echo_green "Creating arepo images..."
    if [ $(type -t on_submit_image) ]; then
        on_submit_image
    fi
    box="${IMAGE_FLAGS[2]} ${IMAGE_FLAGS[3]} ${IMAGE_FLAGS[4]} ${IMAGE_FLAGS[5]} ${IMAGE_FLAGS[6]} ${IMAGE_FLAGS[7]}"
    for i in $(seq ${IMAGE_FLAGS[0]} ${IMAGE_FLAGS[1]})
    do
	jobcmd="${jobcmd}
${RUN_CMD_SUBMIT} ./Arepo ${PARAM_FILE} 5 $i 1000 1000 0 1 2 ${box} > output/output_img.log"
    done
    rm -f submitIMG*
    submit "IMG" "$jobcmd"
}
submit_cancel()
{
    logFiles=$SUBMIT_LOG*log
    for f in $logFiles; do
	tCancel=$(submit_log_get "Time-Cancel" $f)
	tEnd=$(submit_log_get "Time-End" $f)
	if [ -z "$tCancel" ] && [ -z "$tEnd" ]; then
	    jobid=$(submit_log_get "Job-ID" $f)
	    eval "${CANCEL_CMD} ${jobid}"
	    echo_green "Cancelling the job: ${jobid}"
	    submit_log_add "Time-Cancel: ${CURRENT_TIME}" "$f"
	fi
    done
}
queue_history()
{
    echo_green "Submit log history:"	
    log=$(tail -16 $SIM_LOG)
    echo "$log"
}
queue_running()
{
    queue=$(queue_list)
    while read p; do
	IFS='-' read -ra ADDR <<< "$p"
	queueID="${ADDR[1]//[[:blank:]]/}"
	if [ -n "$queueID" ]; then
	    if [[ $queue == *$queueID* ]]; then
		echo $(echo "$queue" | grep "$queueID") " | ${ADDR[2]}"
	    fi
	fi
    done <$SIM_LOG
    
}
print_submit_stats()
{    
    tSubmit=$(submit_log_get "Time-Submit" $1)
    tCancel=$(submit_log_get "Time-Cancel" $1)
    tStart=$(submit_log_get "Time-Start" $1)
    tEnd=$(submit_log_get "Time-End" $1)
    tNow=$(date '+%s')
    echo "File:     " $1
    echo "Job ID:   " $(submit_log_get "Job-ID" $1)
    echo "Submited:  $(date --date=@${tSubmit})"
    if [ -n "$tStart" ]; then
	echo "Started:   $(date --date=@${tSubmit})"
	dt=$((tSubmit-tSubmit))
	echo "Waiting:   $((dt/3600)):$((dt%3600/60)):$((dt%60))"
	if [ -n "$tEnd" ]; then
	    echo "Ended:    $(date --date=@${tEnd})"
	    dt=$((tEnd-tSubmit))
	    echo "Running:   $((dt/3600)):$((dt%3600/60)):$((dt%60))"
	    dt=$((tEnd-tSubmit))
	    echo "Total:     $((dt/3600)):$((dt%3600/60)):$((dt%60))"
	elif [ -n "$tCancel" ]; then
	    echo "Cancelled: $(date --date=@${tCancel})"
	    dt=$((tCancel-tSubmit))
	    echo "Running:   $((dt/3600)):$((dt%3600/60)):$((dt%60))"
	    dt=$((tCancel-tSubmit))
	    echo "Total:     $((dt/3600)):$((dt%3600/60)):$((dt%60))"
	else
	    dt=$((tNow-tSubmit))
	    IFS=':' read -r -a array <<< "$JOB_WALL_TIME"
	    mdt=$((array[0]*3600+array[1]*60+array[2]))
	    if [ "$dt" -gt "$mdt" ]; then
		echo "Job did not finish within the walltime ${JOB_WALL_TIME}!!"
	    else
		runTime="$((dt/3600)):$((dt%3600/60)):$((dt%60))"
		echo "Running:   $runTime (max ${JOB_WALL_TIME})"
	    fi
	fi
    elif [ -n "$tCancel" ]; then
        dt=$((tCancel-tSubmit))
        echo "Waiting:   $((dt/3600)):$((dt%3600/60)):$((dt%60))"
        echo "Cancelled: $(date --date=@${tCancel})"
    else
        dt=$((tNow-tSubmit))
        echo "Waiting:   $((dt/3600)):$((dt%3600/60)):$((dt%60))"
    fi
}
submit_stats()
{
    logFiles=$(find ./ -name "$SUBMIT_LOG*log")
    if [ -z "$logFiles" ]; then
	echo_red "No submit statistics available..."
    else
	echo_green "Submit statistics:"	
	echo "$logFiles" | while read line; do
	    echo "---"
	    print_submit_stats $line
	done
	echo "---"
	if ls output/snap_* 1> /dev/null 2>&1; then
	    echo "Latest snapshot: " $(find output/snap_* | tail -1)
	fi
    fi
}
queue_avail()
{
    echo_green "Available submit resources:"
    if [ $(type -t on_queue_avail) ]; then
        on_queue_avail
    else
	echo_red "Information not available..."
    fi
}
queue_list()
{
    echo_green "Subimt queue:"
    if [ $(type -t on_queue_list) ]; then
        on_queue_list
    else
	echo_red "Information not available..."
    fi
}

results_sync()
{
    echo_green "Synchronizing results:"
    if [ $(type -t on_results_sync) ]; then
        on_results_sync
    else
	echo_red "No synchronization script available..."
    fi
}

refract()
{
    strFrom="${1}"
    strTo="${2}"

    # look in the particular files
    if [[ -z "${3}" ]]; then
	format="*.py"
    else
	format="${3}"
    fi
    
    # replace everything
    echo -e "${YEL}Changing '${strFrom}' to '${strTo}'${NC}"
    found=$(grep -r --include="$format" "${strFrom}" $DIR_AREPY/python)
    if [[ ! -z $found ]]; then
	echo -e "${YEL}The following strings will be replaced:${NC}"
	echo "$found"
	read -p $'\e[33mAre you sure (Y/n)?\e[0m ' -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]?$ ]]; then
	    echo -e "${YEL}processing...${NC}"
	    sedstring="s/${strFrom}/${strTo}/g"
	    find ./ -iname "$format" -exec sed -i -e "$sedstring" {} \;
	    echo -e "${YEL}done${NC}"
	fi
    else
	echo -e "${YEL}No string was found${NC}"
    fi
}

# Run an interactive session
inter_run()
{
    echo -e "\033[0;33mNumber of nodes:\033[0m"; read nodes
    echo -e "\033[0;33mCores per node:\033[0m"; read ppn
    echo -e "\033[0;33mQueue type:\033[0m"; read type
    echo -e "\033[0;33mWalltime:\033[0m"; read walltime
    on_inter_run
    eval="${INTER_CMD}"
    echo -e "${YEL}$eval${NC}"
    eval "$eval"
}

# Function that initialize the simulation directory
clean_directory()
{
    echo_green "Cleaning directory..."
    rm -f -r submit* *-usedvalues output/* results/* uses-machines.txt *~ \#* WARNINGS $CLEAN_FILES
    if [ $(type -t on_clean_directory) ]; then
	echo_green "Initial directory setup..."
	on_clean_directory
    fi
    if [ -d "output_ini" ]; then
	echo_green "Copying initial snapshot..."
        cd output
        ln -s ../output_ini/* ./
        cd ..
    fi
}
analyze()
{
    if [ $(type -t on_analyze) ]; then
	on_analyze "$@"
    else
	if [ "$1" == "init-proj" ]; then
	    python3 -W ignore $DIR_PYTHON_AREPY/scripy/main.py none "$@"
	elif [ "$1" == "plot" ] && [ "$2" == "" ]; then  # print the available plot classes
	    classes=$(find $DIR_PROJECT/plots -name *.py -exec grep -hr class {} \;) # find all files with classes
	    classes=$(sed 's/class //g; s/apy.scripy.plot//g; s/)://g; s/(/ /g' <<< "$classes") # remove python stuff
	    classes=$(awk 'NF >= 2{t=$2;$2=$1;$1=t};{print}' <<< "$classes") # swap classes names
	    sort <<< "$classes" # sort names
	elif [ $PROJECT_NAME == "none" ]; then
	    echo -e "${RED}Cannot analyze a non-scripy directory!${NC}"	     
	else
	    python3 -W ignore $DIR_PYTHON_AREPY/scripy/main.py $PROJECT_NAME "$@"
	fi
    fi
}
analyze_snaps()
{
    for d in $(find -name output -type d | sort) ; do
	find $d -name snap_* -type f | sort -V | tail -1
    done
}
archive_outputs()
{
    name=$(date +%y%m%d_%H%M)
    name="arch_$name"
    mkdir $name
    mv submit* $name
    mv output/output* $name
}
clean_arepo()
{
    echo_green "Cleaning Arepo build..."
    cd $DIR_AREPO
    make clean
    cd $DIR_PWD
}
compile_arepo()
{
    echo_green "Compiling Arepo..."
    if ! cmp -b $DIR_AREPO/$CONFIG_FILE $CONFIG_FILE
    then
	cp $CONFIG_FILE $DIR_AREPO
    fi
    cd $DIR_AREPO
    make -j build
    cp Arepo $DIR_PWD
    cd $DIR_PWD
}
initialize()  
{
    echo_green "Initializing the directory..."
    if [ ! -d "output" ]; then
	mkdir output
    fi
    if [ ! -d "results" ]; then
	mkdir results
    fi
    if [ ! -d "scripts" ]; then
	mkdir scripts
    fi
    touch scripts/analyze.py
    if [ $(type -t on_initialize) ]; then
	on_initialize
    fi
}

# Additional information
show_params()
{
    echo_green "Simulation settings:"
    echo "Name:                       ${JOB_NAME}"
    echo "Queue:                      ${JOB_TYPE}"
    echo "Wall-time:                  ${JOB_WALL_TIME}"
    echo "Nodes:                      ${NUM_NODES}"
    echo "Processors:                 ${NUM_PROC}" 
    echo_green "Environmental settings:"
    echo "Machine:                    ${MACHINE}"
    echo "Arepo directory:            ${DIR_AREPO}"
    echo "Current directory:          ${DIR_PWD}"
}
show_help()
{
    less $DIR_AREPY/shell/README.md
}

interactive=
filename=~/sysinfo_page.html

while [ "$1" != "" ]; do
    case $1 in
	--plot )                   shift; analyze plot "$@"; break;;
	--debug )                  shift; analyze debug "$@"; break;;
	--movie )                  shift; analyze movie "$@"; break;;
	--show )                   shift; analyze show "$@"; break;;
	--setup )                  shift; analyze setup "$@"; break;;
	--script )                 shift; analyze script "$@"; break;;
	--init-project )           shift; analyze init-proj "$@"; break;;
	--init-plot )              shift; analyze init-plot "$@"; break;;
	--init-setup )             shift; analyze init-setup "$@"; break;;
	--init-script )            shift; analyze init-script "$@"; break;;

	--sync )                   results_sync ;;
	--refract )                shift; refract "$@"; break;;

	-i | --initialize )        initialize ;;
	-d | --clean-dir )         clean_directory ;;

	-as | --analyze-snaps )    analyze_snaps ;;
	-ao | --archive-outputs )  archive_outputs ;;

	-qa | --queue-avail )      queue_avail ;;
	-ql | --queue-list )       queue_list ;;
	-qr | --queue-running )    queue_running ;;
	-qh | --queue-history )    queue_history ;;

	-si | --submit-image )     submit_image ;;
	-ss | --submit-stats )     submit_stats ;;
	-sr | --submit-restart )   submit_restart ;;
	-sc | --submit-cancel )    submit_cancel ;;
	-s | --submit )            submit_run ;;

	-I | --interactive )        inter_run ;;
	
	-ti | --terminal-image )   terminal_image ;;
	-tr | --terminal-restart ) terminal_restart ;;
	-t | --terminal )          terminal_run ;;
	
	-cc | --clean-compile )    clean_arepo 
	                           compile_arepo ;;
        -c | --compile )           compile_arepo ;;

	-p | --params )            show_params ;;
	-h | --help )              show_help ;;
        * ) 
    esac
    shift
done
