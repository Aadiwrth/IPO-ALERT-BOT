#!/usr/bin/env python3
"""
Startup script for IPO Alert Bot
Runs the main.py inside src/ without needing -m
"""

import sys
import os

# Add src/ to sys.path so imports work
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

# Now we can import main directly
from src.main import main

if __name__ == "__main__":
    main()
