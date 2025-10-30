#!/usr/bin/env python3
"""
crontab_setup.py
One-time helper: add (or remove) the daily cron job to run screener.py at 08:00 daily.
Requires the `crontab` package:  pip install python-crontab
"""
import os
import sys
from pathlib import Path
from crontab import CronTab

COMMENT = "TrendEdge-daily-screener"
WRAPPER = Path.home() / "TrendEdge-daily.sh"
PYTHON = sys.executable
PROJECT = Path(__file__).resolve().parents[1]
SHELL_SCRIPT = f"""#!/bin/bash
cd {PROJECT}
{PYTHON} src/screener.py >> logs/cron.log 2>&1
"""

def install():
    # create wrapper script
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