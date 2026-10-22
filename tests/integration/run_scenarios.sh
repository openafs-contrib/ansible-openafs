#!/bin/bash
#
# Run the molecule scenarios given in AFS_SCENARIO, a space separated list of
# scenario names (default role_openafs_krbserver_default).
#
# A single scenario is run in the foreground. When more than one scenario is
# given, the scenarios are run AFS_WORKERS at a time (default 1), the output of
# each scenario is written to logs/<scenario>.log, and the result of each
# scenario is printed when it is done.
#
# Each scenario creates its own instances and podman network, so the
# scenarios can be run in parallel. (The molecule --workers option is not
# used, since it runs all of the scenarios on the instances of the default
# scenario.)
#
set -u

scenarios=(${AFS_SCENARIO:-role_openafs_krbserver_default})
workers=${AFS_WORKERS:-1}
logdir=logs

if [ ${#scenarios[@]} -eq 1 ]; then
    exec python3 -m molecule test -s "${scenarios[0]}"
fi

run_scenario() {
    if python3 -m molecule test -s "$1" > "$logdir/$1.log" 2>&1; then
        echo "PASS $1"
    else
        echo "FAIL $1 (see $logdir/$1.log)"
        return 1
    fi
}
export -f run_scenario
export logdir

mkdir -p "$logdir"
echo "Running ${#scenarios[@]} scenarios, $workers at a time."
printf '%s\n' "${scenarios[@]}" | xargs -P "$workers" -I{} bash -c 'run_scenario "$1"' _ {}
