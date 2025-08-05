#!/usr/bin/env python3
"""
Performance monitoring script for the smoke detection system.
"""

import psutil
import time
import os
import sys

def monitor_performance():
    """Monitor system performance."""
    
    print("=== Performance Monitor ===")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            
            # Get Python processes
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            python_processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            # Clear screen (works on most terminals)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print(f"=== Performance Monitor - {time.strftime('%H:%M:%S')} ===")
            print(f"System CPU: {cpu_percent:.1f}%")
            print(f"System Memory: {memory.percent:.1f}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)")
            print()
            
            print("Top Python Processes:")
            print("PID\t\tCPU%\t\tMemory%\t\tName")
            print("-" * 50)
            
            for proc in python_processes[:5]:  # Show top 5
                if proc['cpu_percent'] > 0:
                    print(f"{proc['pid']}\t\t{proc['cpu_percent']:.1f}%\t\t{proc['memory_percent']:.1f}%\t\t{proc['name']}")
            
            print("\nPress Ctrl+C to stop")
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    monitor_performance() 