# cycle_detector/tests/conftest.py

import sys
import os
import pytest

# Add the parent directory to the Python path to allow imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
