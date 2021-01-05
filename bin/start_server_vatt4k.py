"""
Example script to start an azcam application.

Usage: Execute this file from File Explorer
"""

import os
import sys
from pathlib import Path, PurePosixPath

rootfolder = Path(__file__).resolve().parent.parent
rootfolder = rootfolder / "azcam_vatt/vatt4k"
rootfolder = str(PurePosixPath(rootfolder))

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

imports = f"import sys; sys.path.append('{rootfolder}')"
import_command = f"{imports};import server_vatt4k; from azcam.cli import *"

# execute
cl = (
    f"{python} --profile {profile} "
    f"--TerminalInteractiveShell.term_title_format={profile} {interactive} "
    f'-c "{import_command}" -- {" ".join(arguments)}'
)
os.system(cl)
