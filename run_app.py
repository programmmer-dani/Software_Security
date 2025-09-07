#!/usr/bin/env python3

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.presentation.cli import run

if __name__ == "__main__":
    run()
