# azcamconsole config file for vatt4k

import datetime
import os
import threading

import azcam
import azcam.console
import azcam.shortcuts_console
from azcam_ds9.ds9display import Ds9Display
from azcam_focus.focus import Focus
from azcam_observe.observe import Observe


# ****************************************************************
# files and folders
# ****************************************************************
azcam.db.systemname = "vatt4k"
azcam.db.systemfolder = f"{os.path.dirname(__file__)}"
azcam.db.datafolder = os.path.join("/data", azcam.db.systemname)
parfile = f"{azcam.db.datafolder}/parameters_{azcam.db.systemname}.ini"

# ****************************************************************
# add folders to search path
# ****************************************************************
for p in ["vatt4k"]:
    folder = os.path.join(azcam.db.systemfolder, p)
    azcam.utils.add_searchfolder(folder, 0)
folder = os.path.abspath(os.path.join(azcam.db.systemfolder, "../common"))
azcam.utils.add_searchfolder(folder, 0)

# ****************************************************************
# start logging
# ****************************************************************
tt = datetime.datetime.strftime(datetime.datetime.now(), "%d%b%y_%H%M%S")
azcam.db.logger.logfile = os.path.join(azcam.db.datafolder, "logs", f"console_{tt}.log")
azcam.db.logger.start_logging()
azcam.log(f"Configuring console for {azcam.db.systemname}")

# ****************************************************************
# display
# ****************************************************************
display = Ds9Display()
dthread = threading.Thread(target=display.initialize, args=[])
dthread.start()  # thread just for speed

# ****************************************************************
# focus script
# ****************************************************************
focus = Focus()
azcam.db.cli_cmds["focus"] = focus
focus.focus_component = "telescope"
focus.focus_type = "absolute"

# ****************************************************************
# observe script
# ****************************************************************
observe = Observe()
azcam.db.cli_cmds["observe"] = observe

# ****************************************************************
# try to connect to azcamserver
# ****************************************************************
connected = azcam.api.server.connect(2412)
if connected:
    azcam.log("Connected to azcamserver")
else:
    azcam.log("Not connected to azcamserver")

# ****************************************************************
# read par file
# ****************************************************************
pardict = azcam.api.config.read_parfile(parfile)
azcam.api.config.update_pars(0, "azcamconsole")

# ****************************************************************
# finish
# ****************************************************************
azcam.log("Configuration complete")
