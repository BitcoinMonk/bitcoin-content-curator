#!/usr/bin/env python3
"""
Scheduler for Bitcoin Content Curator

Runs the curator at specified intervals using the schedule library.
Alternative: Use cron or systemd timers instead.
"""

import schedule
import time
import subprocess
import sys
from pathlib import Path


# How often to run (in hours)
RUN_INTERVAL_HOURS = 1


def run_curator():
    """Run the curator script."""
    print(f"\n{'=' * 50}")
    print(f"Running curator at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 50}\n")

    curator_path = Path(__file__).parent / "curator.py"

    try:
        result = subprocess.run(
            [sys.executable, str(curator_path)],
            cwd=str(curator_path.parent),
            capture_output=False
        )
        if result.returncode != 0:
            print(f"Curator exited with code {result.returncode}")
    except Exception as e:
        print(f"Error running curator: {e}")


def main():
    print("Bitcoin Content Curator - Scheduler")
    print(f"Will run every {RUN_INTERVAL_HOURS} hour(s)")
    print("Press Ctrl+C to stop\n")

    # Run immediately on start
    run_curator()

    # Schedule future runs
    schedule.every(RUN_INTERVAL_HOURS).hours.do(run_curator)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScheduler stopped")
