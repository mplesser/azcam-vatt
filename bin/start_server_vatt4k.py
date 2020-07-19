"""
Example script to start an azcam application.

Usage: Execute this file from File Explorer
"""

import os
import sys

rootfolder = "/data/code/azcam-vatt/azcam_vatt/vatt4k"
rootfolder = os.path.abspath(os.path.relpath(rootfolder))
rootfolder = os.path.normpath(rootfolder).replace("\\", "/")

# select which python to use (virtual environments)
python = "ipython.exe"
interactive = "-i"  # "-i" or ""

# parse arguments for command script
if len(sys.argv) > 1:
    # arguments = ["-system VATT4k -data \data\vatt4k"]
    arguments = sys.argv[1:]
else:
    arguments = [""]

profile = "azcamserver"

import_command = f"sys.path.append('{rootfolder}');" f"import azcam_vatt4k_server; from azcam.cli import *"

# execute
cl = (
    f"{python} --profile {profile} "
    f"--TerminalInteractiveShell.term_title_format={profile} {interactive} "
    f'-c "{import_command}" -- {" ".join(arguments)}'
)
os.system(cl)
