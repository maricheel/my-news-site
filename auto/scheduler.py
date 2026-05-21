#!/usr/bin/env python3
"""
Scheduler for automation script
Runs the automation every 45 minutes automatically
"""

import schedule
import time
import sys
from datetime import datetime

# Import the main automation function
from automate_simple import main as run_automation


def job():
    """The job to run on schedule"""
    try:
        run_automation()
    except Exception as e:
        print(f"❌ Job failed with error: {e}")


def start_scheduler(interval_minutes=45):
    """Start the scheduler"""
    
    print("\n" + "="*50)
    print("🤖 AUTOMATION SCHEDULER STARTED")
    print("="*50)
    print(f"⏰ Running every {interval_minutes} minutes")
    print("📍 Press Ctrl+C to stop\n")
    
    # Schedule the job
    schedule.every(interval_minutes).minutes.do(job)
    
    # Run once at startup
    print("🚀 Running initial job...")
    job()
    
    # Keep scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Scheduler stopped by user")
        print("="*50 + "\n")
        sys.exit(0)


if __name__ == '__main__':
    # Default: run every 45 minutes
    interval = 45
    
    # Allow custom interval from command line
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print(f"Usage: python scheduler.py [minutes]")
            print(f"Example: python scheduler.py 45")
            sys.exit(1)
    
    start_scheduler(interval)
