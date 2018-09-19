#!/usr/local/bin/bash

# parse args
while getopts b:d:f:l:o:zt option
do
  case "${option}"
    in
    b) BUCKET=${OPTARG};;
    d) DATE=${OPTARG};;
    f) FILE=${OPTARG};;
    l) LEVEL=${OPTARG};;
    o) OUTPUT=${OPTARG};;
    t) TEST="--test";;
    z) ZEROES="--set-zero-counts";;
  esac
done

if [ $LEVEL == "state" ]
  then
    results_level="state"
    results_filter="state"
    filename="state"
  else
    results_level="RU"
    results_filter="county"
    filename="county"
fi


# if [ $TEST ] ; then
#   export ELEX_RECORDING="flat"
#   export ELEX_RECORDING_DIR="${OUTPUT}/recordings/${DATE}"
# fi

# grab elex results for everything
if [ $FILE ]
  then
    elex results ${DATE} ${TEST} ${ZEROES} --national-only -o json -d ${FILE} > master.json

  else
    elex results ${DATE} ${TEST} ${ZEROES} --national-only --results-level ${results_level} -o json > master_$filename.json
fi

echo "Got results: `date`"

# filter results
echo "Starting filter: `date`"

case $BASH_VERSION in ''|[123].*|4.[01].*) echo "ERROR: Bash 4.2 required" >&2; exit 1;; esac

input_file="master_$filename.json"
[[ -s $input_file ]] || { echo "master.json not a valid file" >&2; exit 1; }

jq_split_script='
def relevantContentOnly:
  { fipscode, level, polid, polnum, precinctsreporting, precinctsreportingpct, precinctstotal, raceid, runoff, statepostal, votecount, votepct, winner };

if (.level != $level) then empty else (
  [.statename, .officeid, (relevantContentOnly | tojson)] | @tsv
) end
'

# Use an associative array to map from state names to output FDs
declare -A out_fds=( )

# Read state / office / line-of-data tuples from our JQ script...
while IFS=$'\t' read -r state office data; do
  # If we don't already have a writer for the current state, start one.
  if [[ ! ${out_fds[$state]} ]]; then
    slug="$(echo -n "${state}" | sed -e 's/[^[:alnum:]]/-/g' \
    | tr -s '-' | tr A-Z a-z)"
    mkdir -p $OUTPUT/election-results/$results_filter/$slug
    exec {new_fd}> >(jq -n '[inputs]' >"$OUTPUT/election-results/$results_filter/$slug/$filename.json")
    out_fds[$state]=$new_fd
  fi
  # If we don't already have a writer for the current state, start one.
  if [[ ! ${out_fds[$office]} ]]; then
    slug="$(echo -n "${office}" | sed -e 's/[^[:alnum:]]/-/g' \
    | tr -s '-' | tr A-Z a-z)"
    mkdir -p $OUTPUT/election-results/$results_filter/$slug
    exec {new_fd}> >(jq -n '[inputs]' >"$OUTPUT/election-results/$results_filter/$slug/$filename.json")
    out_fds[$office]=$new_fd
  fi
  if [[ ! ${out_fds[${state}-${office}]} ]]; then
    stateslug="$(echo -n "${state}" | sed -e 's/[^[:alnum:]]/-/g' \
    | tr -s '-' | tr A-Z a-z)"
    officeslug="$(echo -n "${office}" | sed -e 's/[^[:alnum:]]/-/g' \
    | tr -s '-' | tr A-Z a-z)"
    mkdir -p $OUTPUT/election-results/$results_filter/$stateslug/$officeslug
    exec {new_fd}> >(jq -n '[inputs]' >"$OUTPUT/election-results/$results_filter/$stateslug/$officeslug/$filename.json")
    out_fds[${state}-${office}]=$new_fd
  fi
  # Regardless, send the data to the FD we have for this state
  printf '%s\n' "$data" >&${out_fds[$state]}
  printf '%s\n' "$data" >&${out_fds[$office]}
  printf '%s\n' "$data" >&${out_fds[${state}-${office}]}
done < <(cat "$input_file" | jq -cn --stream 'fromstream(1|truncate_stream(inputs))' | jq -cr "$jq_split_script" --arg level $results_filter) # ...running the JQ script above.

# close output FDs, so the JQ instances all flush
for fd in "${!out_fds[@]}"; do
  exec {fd}>&-
done

echo "Filter finished: `date`"

# deploy to s3
if [ $BUCKET ] ; then
  aws s3 cp ${OUTPUT}/election-results/$results_filter s3://${BUCKET}/election-results/ --recursive --acl "public-read" --cache-control "max-age=5"
fi

cp master_$filename.json reup_$filename.json