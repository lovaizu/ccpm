"""Puts this folder on the path, so that each test reaches lanetest, which puts Lane's code
there."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
