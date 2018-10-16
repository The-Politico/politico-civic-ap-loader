#!/usr/local/bin/bash

# parse args
while getopts b:d:f:l:o:zt option
do
  case "${option}"
    in
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


if [ $TEST ] ; then
  today=$(date +%Y-%m-%d)

  export ELEX_RECORDING="flat"
  export ELEX_RECORDING_DIR="${OUTPUT}/recordings/${DATE}/${today}/${filename}"
fi

# grab elex results for everything
if [ $FILE ]
  then
    elex results ${DATE} ${TEST} ${ZEROES} --national-only -o json -d ${FILE} > master_$filename.json

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
  { fipscode, level, party, polid, polnum, precinctsreporting, precinctsreportingpct, precinctstotal, raceid, runoff, seatnum, statepostal, votecount, votepct, winner };

if (.level != $level) then empty else (
  [.statename, .officeid, (relevantContentOnly | tojson)] | @tsv
) end
'

# Use an associative array to map from state names to output FDs
declare -A out_fds=( )

# Read state / office / line-of-data tuples from our JQ script...
while IFS=$'\t' read -r state office data; do
  if [ $office == 'G' ]; then
    officename='governor'
  elif [ $office == 'H' ]; then
    officename='house'
  elif [ $office == 'S' ]; then
    officename='senate'
  fi

  # If we don't already have a writer for the current state, start one.
  if [[ ! ${out_fds[$state]} ]]; then
    slug="$(echo -n "${state}" | sed -e 's/[^[:alnum:]]/-/g' \
    | tr -s '-' | tr A-Z a-z)"

    mkdir -p $OUTPUT/election-results/$results_filter/$slug
    exec {new_fd}> >(jq -n '[inputs]' >"$OUTPUT/election-results/$results_filter/$slug/$filename.json")

    out_fds[$state]=$new_fd
  fi
  # If we don't already have a writer for the current office, start one.
  if [[ ! ${out_fds[$officename]} ]]; then
    mkdir -p $OUTPUT/election-results/$results_filter/$officename
    exec {new_fd}> >(jq -n '[inputs]' >"$OUTPUT/election-results/$results_filter/$officename/$filename.json")

    out_fds[$officename]=$new_fd
  fi
  # If we don't already have a writer for the current state office, start one.
  if [[ ! ${out_fds[${state}-${officename}]} ]]; then
    stateslug="$(echo -n "${state}" | sed -e 's/[^[:alnum:]]/-/g' \
    | tr -s '-' | tr A-Z a-z)"

    mkdir -p $OUTPUT/election-results/$results_filter/$stateslug/$officename
    exec {new_fd}> >(jq -n '[inputs]' >"$OUTPUT/election-results/$results_filter/$stateslug/$officename/$filename.json")

    out_fds[${state}-${officename}]=$new_fd
  fi

  # Regardless, send the data to the FDs we have for this row
  printf '%s\n' "$data" >&${out_fds[$state]}
  printf '%s\n' "$data" >&${out_fds[$officename]}
  printf '%s\n' "$data" >&${out_fds[${state}-${officename}]}
done < <(cat "$input_file" | jq -cn --stream 'fromstream(1|truncate_stream(inputs))' | jq -cr "$jq_split_script" --arg level $results_filter)

# close output FDs, so the JQ instances all flush
for fd in "${!out_fds[@]}"; do
  exec {fd}>&-
done

echo "Filter finished: `date`"

cp master_$filename.json reup_$filename.json