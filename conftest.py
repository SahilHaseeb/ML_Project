# conftest.py — tells pytest that the project root is on the Python path
# This file is automatically loaded by pytest before any tests run.

import sys
import os

# Add the project root to sys.path so that "from src.xxx import yyy" works
sys.path.insert(0, os.path.dirname(__file__))
