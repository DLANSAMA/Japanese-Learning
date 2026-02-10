#!/usr/bin/env python3
import sys
import os

# Ensure src is in path
sys.path.append(os.path.dirname(__file__))

from src.main import main

if __name__ == "__main__":
    main()
