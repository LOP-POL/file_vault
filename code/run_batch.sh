#!/bin/bash
#
# run_batch.sh
#
# Runs pace2D on every *.infile in this script's own directory, one at a
# time. Continues to the next infile even if one fails. Sends a start email
# and a done/failed email for each simulation via Gmail SMTP + curl (app
# password), with that simulation's own log included in the email body and
# attached as a file.
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

set -uo pipefail

# Pick up variables defined in ~/.bashrc (harmless if nothing new is exported,
# e.g. if you already exported them in this shell).
source ~/.bashrc 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
MASTER_LOG="$LOG_DIR/batch_run_$(date +%Y_%m_%d_%H:%M:%S).log"

# Max lines of a per-test log to inline in the email body.
MAX_BODY_LOG_LINES=500

# Max raw (pre-base64) attachment size in bytes. Base64 inflates size by
# ~37%, and Gmail's overall message limit is ~25MB, so 15MB raw keeps the
# encoded attachment plus headers comfortably under that limit. If a log
# exceeds this, a truncated (head + tail) version is attached instead and
# the full log is left in place on disk.
MAX_ATTACHMENT_BYTES=$((15 * 1024 * 1024))

# How many lines to keep from the start/end of an oversized log when
# building the truncated version that gets attached.
TRUNCATED_HEAD_LINES=1000
TRUNCATED_TAIL_LINES=1000

# --- Sanity-check required variables ---------------------------------------
: "${data_dir:?data_dir is not set. Export it before running this script.}"
: "${timestamp:?timestamp is not set. Export it before running this script.}"
: "${pace2D_bin:?pace2D_bin is not set. Export it before running this script.}"
: "${app_password:?app_password is not set. Export it before running this script.}"
: "${gmail_address:?gmail_address is not set. Export it before running this script.}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$MASTER_LOG"
}

# --- Email helper ------------------------------------------------------------
# send_email <subject> <body> [attachment_path]
# If attachment_path is given, its contents are attached as a file AND
# (truncated to MAX_BODY_LOG_LINES) included inline in the body.
send_email() {
    local subject="$1"
    local body="$2"
    local attachment="${3:-}"
    local boundary="====batch-email-$(date +%s%N)===="
    local tmp_msg
    tmp_msg="$(mktemp)"

    # If an attachment was given, decide whether it needs truncating so the
    # email doesn't blow past Gmail's size limit.
    local attach_to_send=""
    local truncated_tmp=""
    local truncated_note=""

    if [ -n "$attachment" ] && [ -f "$attachment" ]; then
        local size
        size=$(stat -c%s "$attachment" 2>/dev/null || wc -c < "$attachment")

        if [ "$size" -gt "$MAX_ATTACHMENT_BYTES" ]; then
            truncated_tmp="$(mktemp)"
            {
                echo "===== LOG TRUNCATED FOR EMAIL ====="
                echo "Original log is ${size} bytes, which exceeds the ${MAX_ATTACHMENT_BYTES}-byte email attachment limit."
                echo "The full, untruncated log remains on disk at: $attachment"
                echo
                echo "----- first ${TRUNCATED_HEAD_LINES} lines -----"
                head -n "$TRUNCATED_HEAD_LINES" "$attachment"
                echo
                echo "----- [ ... middle of log omitted ... ] -----"
                echo
                echo "----- last ${TRUNCATED_TAIL_LINES} lines -----"
                tail -n "$TRUNCATED_TAIL_LINES" "$attachment"
            } > "$truncated_tmp"
            attach_to_send="$truncated_tmp"
            truncated_note="Log truncated for email: original is ${size} bytes (limit ${MAX_ATTACHMENT_BYTES} bytes). Full log at: $attachment"
        else
            attach_to_send="$attachment"
        fi
    fi

    {
        printf 'From: %s\r\n' "$gmail_address"
        printf 'To: %s\r\n' "$gmail_address"
        printf 'Subject: %s\r\n' "$subject"
        printf 'MIME-Version: 1.0\r\n'
        printf 'Content-Type: multipart/mixed; boundary="%s"\r\n' "$boundary"
        printf '\r\n'

        printf -- '--%s\r\n' "$boundary"
        printf 'Content-Type: text/plain; charset="UTF-8"\r\n\r\n'
        printf '%s\r\n' "$body"
        if [ -n "$truncated_note" ]; then
            printf '\r\nNOTE: %s\r\n' "$truncated_note"
        fi

        if [ -n "$attachment" ] && [ -f "$attachment" ]; then
            printf '\r\n----- log excerpt (last %s lines) -----\r\n' "$MAX_BODY_LOG_LINES"
            tail -n "$MAX_BODY_LOG_LINES" "$attachment" | sed 's/$/\r/'
            printf '\r\n----- end log excerpt -----\r\n\r\n'
        fi

        if [ -n "$attach_to_send" ]; then
            printf -- '--%s\r\n' "$boundary"
            printf 'Content-Type: text/plain; name="%s"\r\n' "$(basename "$attachment")"
            printf 'Content-Transfer-Encoding: base64\r\n'
            printf 'Content-Disposition: attachment; filename="%s"\r\n\r\n' "$(basename "$attachment")"
            base64 "$attach_to_send"
            printf '\r\n'
        fi

        printf -- '--%s--\r\n' "$boundary"
    } > "$tmp_msg"

    if ! curl --silent --show-error \
        --url "smtps://smtp.gmail.com:465" \
        --ssl-reqd \
        --mail-from "$gmail_address" \
        --mail-rcpt "$gmail_address" \
        --user "${gmail_address}:${app_password}" \
        --upload-file "$tmp_msg" \
        >> "$MASTER_LOG" 2>&1
    then
        log "WARNING: failed to send email with subject '$subject' (see $MASTER_LOG for curl output)"
    fi

    rm -f "$tmp_msg"
    [ -n "$truncated_tmp" ] && rm -f "$truncated_tmp"
}

# --- Collect infiles ---------------------------------------------------------
shopt -s nullglob
infiles=("$SCRIPT_DIR"/*.infile)

if [ ${#infiles[@]} -eq 0 ]; then
    log "No .infile files found in $SCRIPT_DIR. Exiting."
    exit 1
fi

log "Found ${#infiles[@]} infile(s) in $SCRIPT_DIR."

failed_tests=()

# --- Main loop ---------------------------------------------------------------
for infile in "${infiles[@]}"; do
    infile_name="$(basename "$infile")"
    test_name="${infile_name%.infile}"
    output_dir="${data_dir}/${test_name}_${timestamp}"
    run_log="$LOG_DIR/${test_name}_${timestamp}.log"

    start_time="$(date '+%Y-%m-%d %H:%M:%S')"
    log "STARTING: $infile_name -> $output_dir (log: $run_log)"
    send_email "Simulation STARTED: $test_name" \
"Started at: $start_time
Infile: $infile_name
Output dir: $output_dir
Run log: $run_log"

    # This test's own log, separate from the master log, so it can be
    # emailed/attached on its own once the run finishes.
    mpirun -np 4 "$pace2D_bin" -I "$infile" -P "$output_dir" -f > "$run_log" 2>&1
    exit_code=$?

    end_time="$(date '+%Y-%m-%d %H:%M:%S')"

    if [ "$exit_code" -eq 0 ]; then
        log "DONE: $infile_name"
        send_email "Simulation DONE: $test_name" \
"Finished at: $end_time
Infile: $infile_name
Output dir: $output_dir
Status: SUCCESS" \
            "$run_log"
    else
        log "FAILED: $infile_name (exit code $exit_code) - continuing with remaining infiles"
        failed_tests+=("$test_name")
        send_email "Simulation FAILED: $test_name" \
"Finished at: $end_time
Infile: $infile_name
Output dir: $output_dir
Status: FAILED (exit code $exit_code)
Continuing with the remaining infiles." \
            "$run_log"
    fi
done

log "All simulations complete."

if [ ${#failed_tests[@]} -gt 0 ]; then
    summary_status="COMPLETED WITH FAILURES: ${failed_tests[*]}"
else
    summary_status="ALL SUCCEEDED"
fi

send_email "Batch run complete: $summary_status" \
"All ${#infiles[@]} simulation(s) finished at $(date '+%Y-%m-%d %H:%M:%S').
Status: $summary_status
Master log: $MASTER_LOG
Per-test logs are in: $LOG_DIR"
