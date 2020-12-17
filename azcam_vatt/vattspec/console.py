# azcamconsole config file for vattspec


import datetime
import os
import threading

import azcam
import azcam.console
import azcam.shortcuts
from azcam_ds9.ds9display import Ds9Display
from azcam_focus.focus import Focus


# ****************************************************************
# files and folders
# ****************************************************************
azcam.db.systemname = "vattspec"
azcam.db.systemfolder = os.path.dirname(__file__)
azcam.db.datafolder = os.path.join("/data", azcam.db.systemname)
azcam.db.parfile = os.path.join(azcam.db.datafolder, f"parameters_{azcam.db.systemname}.ini")

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
pardict = azcam.api.config.parfile_read(azcam.db.parfile)["azcamconsole"]
azcam.utils.update_pars(0, pardict)
wd = azcam.api.config.get_par(pardict, "wd", "default")
azcam.utils.curdir(wd)

# ****************************************************************
# finish
# ****************************************************************
azcam.log("Configuration complete")
