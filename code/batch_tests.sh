#!/bin/bash
#
# run_batch.sh
#
# Runs pace2D on every *.infile in this script's own directory, one at a
# time, and sends a start / done (or failed) email for each simulation via
# Gmail SMTP + curl, using an app password.
#
# Expects the following to already be set (e.g. exported from ~/.bashrc):
#   data_dir       - base directory to write simulation output into
#   timestamp      - timestamp string appended to each output folder name
#   pace2D_bin     - path to the pace2D binary
#   app_password   - Gmail app password
#   gmail_address  - Gmail address used as BOTH sender and recipient
#
# Usage: place this script alongside your *.infile files and run it, e.g.
#   bash run_batch.sh
# or make it executable and run ./run_batch.sh

set -uo pipefail

# Try to pick up variables defined in ~/.bashrc (harmless if it doesn't
# export anything new, e.g. if you already exported them in this shell).
source ~/.bashrc 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/batch_run_$(date +%Y_%m_%d_%H%:M%:S).log"

# --- Sanity-check required variables ---------------------------------------
: "${data_dir:?data_dir is not set. Export it before running this script.}"
: "${timestamp:?timestamp is not set. Export it before running this script.}"
: "${pace2D_bin:?pace2D_bin is not set. Export it before running this script.}"
: "${app_password:?app_password is not set. Export it before running this script.}"
: "${gmail_address:?gmail_address is not set. Export it before running this script.}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# --- Email helper -----------------------------------------------------------
send_email() {
    local subject="$1"
    local body="$2"
    local email_content
    email_content=$(printf 'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s\r\n' \
        "$gmail_address" "$gmail_address" "$subject" "$body")

    if ! curl --silent --show-error \
        --url "smtps://smtp.gmail.com:465" \
        --ssl-reqd \
        --mail-from "$gmail_address" \
        --mail-rcpt "$gmail_address" \
        --user "${gmail_address}:${app_password}" \
        --upload-file <(printf '%s' "$email_content") \
        >> "$LOG_FILE" 2>&1
    then
        log "WARNING: failed to send email with subject '$subject' (see $LOG_FILE for curl output)"
    fi
}

# --- Collect infiles ---------------------------------------------------------
shopt -s nullglob
infiles=("$SCRIPT_DIR"/*.infile)

if [ ${#infiles[@]} -eq 0 ]; then
    log "No .infile files found in $SCRIPT_DIR. Exiting."
    exit 1
fi

log "Found ${#infiles[@]} infile(s) in $SCRIPT_DIR."

# --- Main loop ---------------------------------------------------------------
for infile in "${infiles[@]}"; do
    infile_name="$(basename "$infile")"
    test_name="${infile_name%.infile}"
    output_dir="${data_dir}/${test_name}_${timestamp}"

    start_time="$(date '+%Y-%m-%d %H:%M:%S')"
    log "STARTING: $infile_name -> $output_dir"
    send_email "Simulation STARTED: $test_name" \
"Started at: $start_time
Infile: $infile_name
Output dir: $output_dir"

    mpirun -np 4 "$pace2D_bin" -I "$infile" -P "$output_dir" -f >> "$LOG_FILE" 2>&1
    exit_code=$?

    end_time="$(date '+%Y-%m-%d %H:%M:%S')"

    if [ "$exit_code" -eq 0 ]; then
        log "DONE: $infile_name"
        send_email "Simulation DONE: $test_name" \
"Finished at: $end_time
Infile: $infile_name
Output dir: $output_dir
Status: SUCCESS"
    else
        log "FAILED: $infile_name (exit code $exit_code)"
        send_email "Simulation FAILED: $test_name" \
"Finished at: $end_time
Infile: $infile_name
Output dir: $output_dir
Status: FAILED (exit code $exit_code)"
    fi
done

log "All simulations complete."
send_email "Batch run complete" \
"All ${#infiles[@]} simulation(s) finished at $(date '+%Y-%m-%d %H:%M:%S').
Log file: $LOG_FILE"