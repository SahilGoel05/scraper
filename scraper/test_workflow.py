#!/usr/bin/env python3
"""
Test script to simulate GitHub Actions workflow locally.
This script runs the scraper and commits changes if any are found.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return None

def check_git_status():
    """Check if there are any uncommitted changes."""
    status = run_command("git status --porcelain")
    return bool(status)

def commit_changes():
    """Commit any changes to the data directory."""
    # Check if there are changes in the data directory
    data_status = run_command("git status --porcelain scraper/data/")
    if not data_status:
        print("No changes in data directory to commit.")
        return False
    
    # Add and commit changes
    print("Changes detected in data directory. Committing...")
    
    # Add the data directory
    run_command("git add scraper/data/")
    
    # Create commit message with timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    commit_msg = f"🤖 Automated scraper update - {timestamp}"
    
    # Commit
    result = run_command(f'git commit -m "{commit_msg}"')
    if result:
        print(f"Successfully committed: {commit_msg}")
        return True
    else:
        print("Failed to commit changes.")
        return False

def main():
    """Main workflow simulation."""
    print("🚀 Starting GitHub Actions workflow simulation...")
    
    # Change to scraper directory
    scraper_dir = Path(__file__).parent
    os.chdir(scraper_dir)
    
    # Step 1: Install dependencies
    print("\n📦 Installing dependencies...")
    result = run_command("pip install -r requirements.txt")
    if not result:
        print("Failed to install dependencies.")
        return 1
    
    # Step 2: Run scraper
    print("\n🕷️ Running scraper...")
    result = run_command("python scraper.py")
    if not result:
        print("Failed to run scraper.")
        return 1
    
    # Step 3: Check for changes
    print("\n🔍 Checking for changes...")
    os.chdir("..")  # Go back to repository root
    has_changes = check_git_status()
    
    if has_changes:
        print("Changes detected!")
        
        # Step 4: Commit changes
        print("\n💾 Committing changes...")
        success = commit_changes()
        if success:
            print("\n✅ Workflow completed successfully!")
            return 0
        else:
            print("\n❌ Failed to commit changes.")
            return 1
    else:
        print("No changes detected. Workflow completed successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 
