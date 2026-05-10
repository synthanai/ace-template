#!/bin/bash
# ACE HARNESS: 10_CRON_CHOREOGRAPHY | LAUNCHER
# Status: CANONICAL
# Purpose: Shell wrapper to trigger the choreographer via OS crontab.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Triggering Nightly Batch Rebuild & Queue Process..."
python3 "$DIR/choreographer.py"
echo "Batch Complete."
