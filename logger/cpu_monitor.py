#!/usr/bin/env python3
"""
Simple CPU monitoring for the smoke detection system.
"""

import psutil
import time
import os

def monitor_cpu():
    """Monitor CPU usage of the main process."""
    
    print("=== CPU Monitor ===")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Find the main.py process
            main_process = None
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'Python' and any('main.py' in cmd for cmd in proc.info['cmdline'] if cmd):
                        main_process = proc
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if main_process:
                cpu_percent = main_process.cpu_percent()
                memory_percent = main_process.memory_percent()
                memory_mb = main_process.memory_info().rss / 1024 / 1024
                
                print(f"\r[{time.strftime('%H:%M:%S')}] Main Process: CPU {cpu_percent:.1f}% | Memory {memory_percent:.1f}% ({memory_mb:.0f}MB)", end='', flush=True)
            else:
                print(f"\r[{time.strftime('%H:%M:%S')}] Main process not found", end='', flush=True)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    monitor_cpu() 