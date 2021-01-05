# azcamconsole config file for vattspec


import datetime
import os
import threading

import azcam
import azcam.console
import azcam.shortcuts_console
from azcam_ds9.ds9display import Ds9Display
from azcam_focus.focus import Focus


# ****************************************************************
# files and folders
# ****************************************************************
azcam.db.systemname = "vattspec"
azcam.db.systemfolder = os.path.dirname(__file__)
azcam.db.datafolder = os.path.join("/data", azcam.db.systemname)
parfile = os.path.join(azcam.db.datafolder, f"parameters_{azcam.db.systemname}.ini")

# ****************************************************************
# add folders to search path
# ****************************************************************
for p in ["vattspec"]:
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
# try to connect to azcamserver
# ****************************************************************
connected = azcam.api.server.connect(port=2412)
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
