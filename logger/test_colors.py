#!/usr/bin/env python3
"""
Test script to check if colors work in the terminal.
"""

import os
import sys

def test_colors():
    """Test if colors work in the terminal."""
    
    # Check if we're in a terminal
    is_tty = sys.stdout.isatty()
    print(f"Terminal detected: {is_tty}")
    print(f"TERM environment: {os.environ.get('TERM', 'Not set')}")
    
    # Test basic colors
    colors = {
        'red': '\033[31m',
        'green': '\033[32m', 
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'reset': '\033[0m'
    }
    
    print("\nTesting colors:")
    for name, code in colors.items():
        if name != 'reset':
            print(f"{code}{name}{colors['reset']}", end=' ')
    
    print("\n\nTesting with force:")
    # Force colors
    os.environ['FORCE_COLOR'] = '1'
    
    for name, code in colors.items():
        if name != 'reset':
            print(f"{code}{name}{colors['reset']}", end=' ')
    
    print("\n")

if __name__ == "__main__":
    test_colors() 