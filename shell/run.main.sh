#!/bin/bash
#set -e  # exit always if there is some error

# Variables that can be overwritten in 'run.sh'
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

AREPO_DIR=${AREPO_DIR:-"./arepo"}              # directory with the arepo source code
FLAGS_RUN=${FLAGS_RUN:-""}                     # arepo run flags
FLAGS_RESTART=${FLAGS_RESTART:-"1"}            # arepo restart flags
PARAM_FILE=${PARAM_FILE:-"param.txt"}          # arepo parameter file
CONFIG_FILE=${CONFIG_FILE:-"Config.sh"}        # arepo configuration file
DIR_PROJECT=${DIR_PROJECT:-"tmp"}              # analyze script
CLEAN_FILES=${CLEAN_FILES:-""}                 # additional files to be cleaned

IMAGE_NODES=${IMAGE_NODES:-1}                    # number of nodes
IMAGE_PROC=${IMAGE_PROC:-16}                     # number of processors per node
IMAGE_WALLTIME=${IMAGE_WALLTIME:-"1:00:00"}      # wall time
IMAGE_TYPE=${IMAGE_TYPE:-"standard"}             # type of nodes
IMAGE_FLAGS=${IMAGE_FLAGS:-"(0 100 0 1 0 1 0 1"} # arepo image flags

# Local variables
THIS_DIR=$(pwd)                                # path to the simulation directory
WORK_DIR=${WORK_DIR:-$(dirname $PWD)}          # main directory with simulations
SIM_NAME=${THIS_DIR#*$WORK_DIR}                # name of the simulation (path within the work dir.)
CURRENT_TIME=$(date '+%s')                     # current date stemp
SIM_LOG=${SIM_LOG:-$HOME/.arepy/submitlog} # path to the file that logs the submit times

RED='\e[31m'                                   # bash output mark for a red color
GRE='\033[0;32m'                               # bash output mark for a green color
YEL='\033[0;33m'
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
cd ${THIS_DIR}
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
    logmsg="$(date) - ${jobID} - ${SIM_NAME}"
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
submit_log()
{
    echo_green "Submit logs:"	
    log=$(tail -16 $SIM_LOG)
    echo "$log"
}
submit_running()
{
    queue=$(submit_queue)
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
submit_avail()
{
    echo_green "Available submit resources:"
    if [ $(type -t on_submit_avail) ]; then
        on_submit_avail
    else
	echo_red "Information not available..."
    fi
}
submit_queue()
{
    echo_green "Subimt queue:"
    if [ $(type -t on_submit_queue) ]; then
        on_submit_queue
    else
	echo_red "Information not available..."
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
	if [ $DIR_PROJECT == "none" ]
	then
	    echo -e "${RED}Cannot analyze a non-scripy directory!${NC}"
	else
	    python3 -W ignore $DIR_AREPY/scripy/main.py $DIR_PROJECT "$@"
	fi
    fi
}
analyze_snaps()
{
    for d in $(find -name output -type d | sort) ; do
	find $d -name snap_* -type f | sort | tail -1
    done
}
clean_arepo()
{
    echo_green "Cleaning Arepo build..."
    cd $AREPO_DIR
    make clean
    cd $THIS_DIR
}
compile_arepo()
{
    echo_green "Compiling Arepo..."
    if ! cmp -b $AREPO_DIR/$CONFIG_FILE $CONFIG_FILE
    then
	cp $CONFIG_FILE $AREPO_DIR
    fi
    cd $AREPO_DIR
    make -j build
    cp Arepo $THIS_DIR
    cd $THIS_DIR
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
    echo "Arepo directory:            ${AREPO_DIR}"
    echo "Work directory:             ${WORK_DIR}"
    echo "Current directory:          ${THIS_DIR}"
}
show_help()
{
    echo_green "Arepo run.sh script options:"
    echo "--plot <script>             run scripy plot scripts"
    echo "--setup <sim> [<part>]      run scripy setup scripts"
    echo "--init-proj                 initialize scripy project directory"
    echo "--init-plot <name>          initialize a new scripy plot"
    echo "--init-setup <name>         initialize a new setup"
    echo "-i  | --initialize          creates output/results/scripts directories"
    echo "-d  | --clean-dir           delete all Arepo runtime files"
    echo "-as | --analyze-snaps       finds the last created snapshots in all subfolders"
    echo "-a  | --analyze <script> [<args>...] run the scripts/analyze.py script"
    echo "-sa | --submit-avail        show available resources on the cluster"
    echo "-sq | --submit-queue        show queue information on the cluster"
    echo "-si | --submit-image        submit a job that creates arepo images"
    echo "-sl | --submit-log          show simulation history log"
    echo "-slr | --submit-log-running show running simulation"
    echo "-ss | --submit-stats        show simulation stats"
    echo "-sr | --submit-restart      submit a restarted job"
    echo "-sc | --submit-cancel       cancel submited job"
    echo "-s  | --submit              submit a new job"
    echo "-I  | --inter-sess          query for an interactive session"
    echo "-ri | --terminal-image      create a custom arepo image"
    echo "-rr | --terminal-restart    restart job in a terminal"
    echo "-r  | --terminal            run job in a terminal"
    echo "-cc | --clean-compile       clean Arepo directory and recompile"
    echo "-c  | --compile             compile Arepo"
    echo "-h  | --help                show this help"
}

interactive=
filename=~/sysinfo_page.html

while [ "$1" != "" ]; do
    case $1 in
        -a | --analyze )           shift; analyze "$@"; break;;
	--plot )                   shift; analyze plot "$@"; break;;
	--debug )                  shift; analyze debug "$@"; break;;
	--movie )                  shift; analyze movie "$@"; break;;
	--show )                   shift; analyze show "$@"; break;;
	--setup )                  shift; analyze setup "$@"; break;;
	--script )                 shift; analyze script "$@"; break;;
	--init-proj )              shift; analyze init-proj "$@"; break;;
	--init-plot )              shift; analyze init-plot "$@"; break;;
	--init-setup )             shift; analyze init-setup "$@"; break;;
	--init-script )            shift; analyze init-script "$@"; break;;

	-i | --initialize )        initialize ;;
	-d | --clean-dir )         clean_directory ;;

	-as | --analyze-snaps )    analyze_snaps ;;
	
	-sa | --submit-avali )     submit_avail ;;
	-sq | --submit-queue )     submit_queue ;;
	-si | --submit-image )     submit_image ;;
	-sl | --submit-log )       submit_log ;;
	-slr | --submit-running)   submit_running ;;
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
