#!/usr/bin/env python3
"""
Auto-commit script for smoke detection system
Automatically commits and pushes changes to Git
"""

import subprocess
import sys
import os
from datetime import datetime
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, capture_output=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        logger.error(f"Error running command '{command}': {e}")
        return False, "", str(e)

def check_for_changes():
    """Check if there are any uncommitted changes"""
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        logger.error(f"Error checking git status: {stderr}")
        return False
    
    return bool(stdout.strip())

def auto_commit(message="Auto-save changes"):
    """Automatically commit and push changes"""
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        logger.error("Not in a git repository")
        return False
    
    # Check for changes
    if not check_for_changes():
        logger.info("No changes to commit")
        return True
    
    # Add all changes
    logger.info("Adding changes to staging area...")
    success, stdout, stderr = run_command("git add .")
    if not success:
        logger.error(f"Error adding files: {stderr}")
        return False
    
    # Create commit message with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"[AUTO] {message} - {timestamp}"
    
    # Commit changes
    logger.info(f"Committing changes: {commit_message}")
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success:
        logger.error(f"Error committing changes: {stderr}")
        return False
    
    # Check if remote is configured
    success, stdout, stderr = run_command("git remote get-url origin")
    if success:
        # Push to remote
        logger.info("Pushing to remote repository...")
        success, stdout, stderr = run_command("git push origin main")
        if not success:
            logger.error(f"Error pushing to remote: {stderr}")
            return False
        logger.info("Successfully pushed to remote")
    else:
        logger.info("No remote repository configured. Skipping push.")
    
    logger.info("Auto-commit completed successfully!")
    return True

def watch_and_auto_commit(interval=300, message="Auto-save changes"):
    """
    Watch for changes and auto-commit every interval seconds
    
    Args:
        interval (int): Time between auto-commits in seconds (default: 5 minutes)
        message (str): Commit message prefix
    """
    logger.info(f"Starting auto-commit watcher (interval: {interval}s)")
    
    try:
        while True:
            if check_for_changes():
                logger.info("Changes detected, auto-committing...")
                auto_commit(message)
            else:
                logger.debug("No changes detected")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Auto-commit watcher stopped by user")
    except Exception as e:
        logger.error(f"Error in auto-commit watcher: {e}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/auto_commit.py commit \"Your message\"")
        print("  python scripts/auto_commit.py watch [interval] [message]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "commit":
        message = sys.argv[2] if len(sys.argv) > 2 else "Auto-save changes"
        success = auto_commit(message)
        sys.exit(0 if success else 1)
    
    elif command == "watch":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        message = sys.argv[3] if len(sys.argv) > 3 else "Auto-save changes"
        watch_and_auto_commit(interval, message)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 