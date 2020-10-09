"""
Script to start an azcam application.

Usage: Execute this file from File Explorer
"""

import os
import sys

# select which python to use (virtual environments)
python = "ipython.exe"
interactive = "-i"  # "-i" or ""

# parse arguments for command script
if len(sys.argv) > 1:
    arguments = sys.argv[1:]
else:
    # arguments = ["-system VIRUS -data \data"]
    arguments = [""]

profile = "azcamconsole"

import_command = f"import azcam_vatt.vatt4k.console; from azcam.cli import *"

# execute
cl = (
    f"{python} --profile {profile} "
    f"--TerminalInteractiveShell.term_title_format={profile} {interactive} "
    f'-c "{import_command}" -- {" ".join(arguments)}'
)
os.system(cl)
