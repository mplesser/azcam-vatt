import datetime
import os
import sys

import azcam
import azcam.server
import azcam.shortcuts_server
from azcam.cmdserver import CommandServer
from azcam.system import System
from azcam.instrument import Instrument
from azcam_monitor.monitorinterface import AzCamMonitorInterface
from azcam_webserver.web_server import WebServer
from azcam_arc.controller_arc import ControllerArc
from azcam_arc.exposure_arc import ExposureArc
from azcam_arc.tempcon_arc import TempConArc
from azcam_ds9.ds9display import Ds9Display
import azcam_exptool
import azcam_status
import azcam_observe.webobs


# ****************************************************************
# parse command line arguments
# ****************************************************************
try:
    i = sys.argv.index("-system")
    option = sys.argv[i + 1]
except ValueError:
    option = "menu"

# ****************************************************************
# define folders for system
# ****************************************************************
azcam.db.systemname = "vatt4k"
azcam.db.servermode = "vatt4k"
azcam.db.systemfolder = os.path.dirname(__file__)
azcam.db.systemfolder = azcam.utils.fix_path(azcam.db.systemfolder)
azcam.db.datafolder = os.path.join("/data", azcam.db.systemname)
azcam.db.datafolder = azcam.utils.fix_path(azcam.db.datafolder)
parfile = os.path.join(azcam.db.datafolder, f"parameters_{azcam.db.systemname}.ini")

# ****************************************************************
# add folders to search path
# ****************************************************************
for p in ["vatt4k"]:
    folder = os.path.join(azcam.db.systemfolder, p)
    azcam.utils.add_searchfolder(folder, 0)
commonfolder = os.path.abspath(os.path.join(azcam.db.systemfolder, "../common"))
azcam.utils.add_searchfolder(commonfolder, 0)

# ****************************************************************
# enable logging
# ****************************************************************
tt = datetime.datetime.strftime(datetime.datetime.now(), "%d%b%y_%H%M%S")
azcam.db.logger.logfile = os.path.join(azcam.db.datafolder, "logs", f"server_{tt}.log")
azcam.db.logger.start_logging()

azcam.log(f"Configuring for vatt4k")

# ****************************************************************
# define and start command server
# ****************************************************************
cmdserver = CommandServer()
cmdserver.port = 2402
azcam.log(f"Starting cmdserver - listening on port {cmdserver.port}")
# cmdserver.welcome_message = "Welcome - azcam-itl server"
cmdserver.start()

# ****************************************************************
# controller
# ****************************************************************
controller = ControllerArc()
azcam.api.controller = controller
controller.timing_board = "gen2"
controller.clock_boards = ["gen2"]
controller.video_boards = ["gen2", "gen2"]
controller.utility_board = "gen2"
controller.set_boards()
controller.camserver.set_server("vattccdc", 2405)
controller.pci_file = os.path.join(
    azcam.db.systemfolder, "dspcode", "dsppci", "pci2.lod"
)
controller.timing_file = os.path.join(
    azcam.db.systemfolder, "dspcode", "dsptiming", "tim2.lod"
)
controller.utility_file = os.path.join(
    azcam.db.systemfolder, "dspcode", "dsputility", "util2.lod"
)
controller.video_gain = 2
controller.video_speed = 2

# ****************************************************************
# temperature controller
# ****************************************************************
tempcon = TempConArc()
azcam.db.tempcon = tempcon
tempcon.set_calibrations([0, 0, 3])
tempcon.set_corrections([2.0, 0.0, 0.0], [1.0, 1.0, 1.0])
tempcon.temperature_correction = 1
tempcon.control_temperature = -115.0

# ****************************************************************
# exposure
# ****************************************************************
exposure = ExposureArc()
azcam.api.exposure = exposure
filetype = "MEF"
exposure.filetype = exposure.filetypes[filetype]
exposure.image.filetype = exposure.filetypes[filetype]
exposure.display_image = 0
exposure.folder = "/mnt/TBArray/images"
remote_imageserver_host = "vattcontrol.vatt"
remote_imageserver_port = 6543
exposure.set_remote_imageserver(remote_imageserver_host, remote_imageserver_port)
# exposure.set_remote_imageserver()

# ****************************************************************
# detector
# ****************************************************************
detector_vatt4k = {
    "name": "vatt4k",
    "description": "STA0500 4064x4064 CCD",
    "ref_pixel": [2032, 2032],
    "format": [4064, 7, 0, 20, 4064, 0, 0, 0, 0],
    "focalplane": [1, 1, 1, 2, "20"],
    "roi": [1, 4064, 1, 4064, 2, 2],
    "ext_position": [[1, 2], [1, 1]],
    "jpg_order": [1, 2],
}
exposure.set_detpars(detector_vatt4k)
# WCS - plate scale (from Rich 19Mar13)
sc = -0.000_052_1
exposure.image.focalplane.wcs.scale1 = [sc, sc]
exposure.image.focalplane.wcs.scale2 = [sc, sc]

# ****************************************************************
# instrument (not used)
# ****************************************************************
instrument = Instrument()

# ****************************************************************
# telescope
# ****************************************************************
from telescope_vatt import VattTCS

telescope = VattTCS()

# ****************************************************************
# system header template
# ****************************************************************
template = os.path.join(
    azcam.db.datafolder, "templates", "FitsTemplate_vatt4k_master.txt"
)
system = System("vatt4k", template)
system.set_keyword("DEWAR", "vatt4k_dewar", "Dewar name")

# ****************************************************************
# display
# ****************************************************************
display = Ds9Display()

# ****************************************************************
# read par file
# ****************************************************************
pardict = azcam.api.config.read_parfile(parfile)
azcam.api.config.update_pars(0, "azcamserver")

# ****************************************************************
# define names to imported into namespace when using cli
# # ****************************************************************
azcam.db.cli_cmds.update({"azcam": azcam})

# ****************************************************************
# web server
# ****************************************************************
webserver = WebServer()
webserver.templates_folder = commonfolder
webserver.index = f"index_VATT.html"
webserver.port = 2403  # common port for all configurations
webserver.start()
azcam_exptool.load()
azcam_status.load()
azcam_observe.webobs.load()

# ****************************************************************
# azcammonitor
# ****************************************************************
monitor = AzCamMonitorInterface()
monitor.proc_path = "/azcam/azcam-vatt/bin/start_server_vatt4k.bat"
monitor.register()

# ****************************************************************
# GUIs
# ****************************************************************
if 0:
    import start_azcamtool

# ****************************************************************
# apps
# ****************************************************************

# ****************************************************************
# finish
# ****************************************************************
azcam.log("Configuration complete")
