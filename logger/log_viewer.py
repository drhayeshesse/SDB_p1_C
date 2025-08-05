#!/usr/bin/env python3
"""
Enhanced log viewer for the smoke detection system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from log_manager import LogManager

def show_help():
    """Show usage information."""
    print("""
=== Log Viewer Commands ===

1. Show log summary:
   python logger/log_viewer.py summary

2. Show camera logs only:
   python logger/log_viewer.py camera [lines]

3. Show smoke detection logs:
   python logger/log_viewer.py smoke [lines]

4. Show processing logs:
   python logger/log_viewer.py processing [lines]

5. Show system logs:
   python logger/log_viewer.py system [lines]

6. Show error logs:
   python logger/log_viewer.py error [lines]

7. Show warning logs:
   python logger/log_viewer.py warning [lines]

8. Show all logs:
   python logger/log_viewer.py all [lines]

Examples:
   python logger/log_viewer.py camera 20
   python logger/log_viewer.py smoke 50
   python logger/log_viewer.py summary
""")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    if command == 'summary':
        LogManager.create_log_summary()
    elif command in ['camera', 'smoke', 'processing', 'system', 'error', 'warning', 'all']:
        LogManager.filter_logs_by_type(command, lines)
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main() 