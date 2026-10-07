#!/usr/bin/env python3
"""Run pith's scenes (scenes.py here) with writ's trial runner, which loads them with pith alone.

    python3 dev/pith/trials/run.py play <scene> <workdir>
    python3 dev/pith/trials/run.py versus <scene> <workdir> <other-workdir>
"""
import os
import runpy
import sys

RUNNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "writ", "trials", "run.py")
sys.path.insert(0, os.path.dirname(RUNNER))
sys.argv[0] = RUNNER
runpy.run_path(RUNNER, run_name="__main__")
