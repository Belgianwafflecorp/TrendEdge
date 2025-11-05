#!/usr/bin/env python3
"""
crontab_setup.py
One-time helper: add (or remove) the daily cron job to run screener.py at 08:00 daily.
"""
import os
import sys
from pathlib import Path
from crontab import CronTab

COMMENT = "TrendEdge-daily-screener"
PROJECT = Path(__file__).resolve().parents[1]
WRAPPER = PROJECT / "TrendEdge-daily.sh"
VENV_PYTHON = PROJECT / ".venv" / "bin" / "python"

SHELL_SCRIPT = f"""#!/bin/bash
set -euo pipefail
cd {PROJECT}
mkdir -p logs

# Use venv Python if available, otherwise fall back to system python3
if [ -f "{VENV_PYTHON}" ]; then
    PYTHON="{VENV_PYTHON}"
else
    PYTHON="python3"
fi

LOG="logs/cron-$(date +%F).log"
"$PYTHON" src/screener.py > "$LOG" 2>&1
# keep only last 7 days of logs
find logs -name 'cron-*.log' -mtime +7 -delete
"""

def install():
    # Create wrapper script in repo root
    WRAPPER.write_text(SHELL_SCRIPT)
    os.chmod(WRAPPER, 0o755)
    print(f"Created wrapper: {WRAPPER}")

    # add to user crontab
    cron = CronTab(user=True)
    # remove any old entry
    cron.remove_all(comment=COMMENT)
    job = cron.new(command=str(WRAPPER), comment=COMMENT)
    job.setall("0 8 * * *")  # 08:00 daily
    cron.write()
    print("Cron job installed: runs 08:00 daily")
    print("List it with:  crontab -l")

def uninstall():
    cron = CronTab(user=True)
    cron.remove_all(comment=COMMENT)
    cron.write()
    print("Cron job removed.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        uninstall()
    else:
        install()