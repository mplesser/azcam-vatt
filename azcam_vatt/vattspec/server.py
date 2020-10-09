import os
import sys
import datetime

from azcam.server import azcam
from azcam.genpars import GenPars
import azcam.shortcuts_server
from azcam.displays.ds9display import Ds9Display
from azcam.header import Header
from azcam.controllers.controller_arc import ControllerArc
from azcam.tempcons.tempcon_arc import TempConArc
from azcam.exposures.exposure_arc import ExposureArc
from azcam.cmdserver import CommandServer
from azcam.instruments.instrument import Instrument
from azcam.webserver.web_server import WebServer
import azcam.monitorinterface

from azcam_vatt.common.telescope_vatt import telescope

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
azcam.db.systemname = "vattspec"
azcam.db.servermode = "vattspec"
azcam.db.systemfolder = os.path.dirname(__file__)
azcam.db.systemfolder = azcam.utils.fix_path(azcam.db.systemfolder)
azcam.db.datafolder = os.path.join("/data", azcam.db.systemname)
azcam.db.datafolder = azcam.utils.fix_path(azcam.db.datafolder)
azcam.db.parfile = os.path.join(azcam.db.datafolder, f"parameters_{azcam.db.systemname}.ini")

# ****************************************************************
# enable logging
# ****************************************************************
tt = datetime.datetime.strftime(datetime.datetime.now(), "%d%b%y_%H%M%S")
azcam.db.logfile = os.path.join(azcam.db.datafolder, "logs", f"server_{tt}.log")
azcam.logging.start_logging(azcam.db.logfile, "123")

azcam.log(f"Configuring for vattspec")

# ****************************************************************
# define and start command server
# ****************************************************************
cmdserver = CommandServer()
cmdserver.port = 2412
azcam.log(f"Starting cmdserver - listening on port {cmdserver.port}")
# cmdserver.welcome_message = "Welcome - azcam-itl server"
cmdserver.start()

# ****************************************************************
# controller
# ****************************************************************
controller = ControllerArc()
controller.timing_board = "gen2"
controller.clock_boards = ["gen2"]
controller.video_boards = ["gen2"]
controller.utility_board = "gen2"
controller.set_boards()
controller.camserver.set_server("vattccdc", 2405)
controller.pci_file = os.path.join(azcam.db.systemfolder, "dspcode", "dsppci", "pci2.lod")
controller.timing_file = os.path.join(azcam.db.systemfolder, "dspcode", "dsptiming", "tim2.lod")
controller.utility_file = os.path.join(azcam.db.systemfolder, "dspcode", "dsputility", "util2.lod")
controller.video_gain = 10
controller.video_speed = 1

# ****************************************************************
# temperature controller
# ****************************************************************
tempcon = TempConArc()
tempcon.set_calibrations([0, 0, 3])
tempcon.set_corrections([2.0, 0.0, 0.0], [1.0, 1.0, 1.0])
tempcon.temperature_correction = 1
tempcon.control_temperature = -115.0

# ****************************************************************
# dewar
# ****************************************************************
controller.header.set_keyword("DEWAR", "vattspec_dewar", "Dewar name")

# ****************************************************************
# exposure
# ****************************************************************
exposure = ExposureArc()
filetype = "FITS"
exposure.filetype = azcam.db.filetypes[filetype]
exposure.image.filetype = azcam.db.filetypes[filetype]
exposure.display_image = 0
exposure.filename.folder = "/mnt/TBArray/images"
remote_imageserver_host = "vattcontrol.vatt"
remote_imageserver_port = 6543
exposure.set_remote_server(remote_imageserver_host, remote_imageserver_port)
# exposure.set_remote_server()

# ****************************************************************
# detector
# ****************************************************************
detector_vattspec = {
    "name": "vattspec",
    "description": "STA0520 2688x512 CCD",
    "ref_pixel": [1344, 256],
    "format": [2688, 16, 0, 20, 512, 0, 0, 0, 0],
    "focalplane": [1, 1, 1, 1, "0"],
    "roi": [1, 2688, 1, 512, 2, 2],
    "extension_position": [[1, 1]],
    "jpg_order": [1],
}
exposure.set_detpars(detector_vattspec)
exposure.image.focalplane.wcs.ctype1 = "LINEAR"
exposure.image.focalplane.wcs.ctype2 = "LINEAR"

# ****************************************************************
# instrument (not used)
# ****************************************************************
instrument = Instrument()

# ****************************************************************
# telescope
# ****************************************************************
telescope = telescope

# ****************************************************************
# system header template
# ****************************************************************
template = os.path.join(azcam.db.datafolder, "templates", "FitsTemplate_vattspec_master.txt")
sysheader = Header("vattspec", template)
sysheader.set_header("system", 0)

# ****************************************************************
# display
# ****************************************************************
display = Ds9Display()

# ****************************************************************
# read par file
# ****************************************************************
genpars = GenPars()
pardict = genpars.parfile_read(azcam.db.parfile)["azcamserver"]
azcam.utils.update_pars(0, pardict)
wd = genpars.get_par(pardict, "wd", "default")
azcam.utils.curdir(wd)

# ****************************************************************
# define names to imported into namespace when using cli
# # ****************************************************************
azcam.db.cli_cmds.update({"azcam": azcam})

# ****************************************************************
# web server
# ****************************************************************
from azcam.webserver.web_server import WebServer

webserver = WebServer()

import azcam_webobs
import azcam_exptool
import azcam_status

webserver.start()

# ****************************************************************
# azcammonitor
# ****************************************************************
monitor = azcam.monitorinterface.MonitorInterface()
monitor.proc_path = "/azcam/azcam-vatt/bin/start_server_vattspec.bat"
monitor.register()

# ****************************************************************
# GUIs
# ****************************************************************
if 1:
    import azcam_vatt.common.start_azcamtool

# ****************************************************************
# apps
# ****************************************************************

# ****************************************************************
# finish
# ****************************************************************
azcam.log("Configuration complete")
