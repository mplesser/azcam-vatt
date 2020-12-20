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
from azcam_vatt.common.telescope_vatt import VattTCS
import azcam_exptool
import azcam_status
import azcam_webobs

# set True for lab testing
LAB = 1

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
azcam.db.logger.logfile = os.path.join(azcam.db.datafolder, "logs", f"server_{tt}.log")
azcam.db.logger.start_logging()

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
controller.pci_file = os.path.join(azcam.db.systemfolder, "dspcode", "dsppci", "pci2.lod")
controller.timing_file = os.path.join(azcam.db.systemfolder, "dspcode", "dsptiming", "tim2.lod")
controller.utility_file = os.path.join(azcam.db.systemfolder, "dspcode", "dsputility", "util2.lod")
controller.video_gain = 10
controller.video_speed = 1
if LAB:
    controller.camserver.set_server("conserver7", 2405)
else:
    controller.camserver.set_server("vattccdc", 2405)

# ****************************************************************
# temperature controller
# ****************************************************************
tempcon = TempConArc()
tempcon.set_calibrations([0, 0, 3])
tempcon.set_corrections([2.0, 0.0, 0.0], [1.0, 1.0, 1.0])
tempcon.temperature_correction = 1
tempcon.control_temperature = -115.0

# ****************************************************************
# exposure
# ****************************************************************
exposure = ExposureArc()
filetype = "FITS"
exposure.filetype = exposure.filetypes[filetype]
exposure.image.filetype = exposure.filetypes[filetype]
exposure.display_image = 0
if LAB:
    exposure.folder = "/data/vattspec"
    exposure.set_remote_imageserver()
else:
    exposure.folder = "/mnt/TBArray/images"
    remote_imageserver_host = "vattcontrol.vatt"
    remote_imageserver_port = 6543
    exposure.set_remote_imageserver(remote_imageserver_host, remote_imageserver_port)

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
    "ext_position": [[1, 1]],
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
telescope = VattTCS()

# ****************************************************************
# system header template
# ****************************************************************
template = os.path.join(azcam.db.datafolder, "templates", "FitsTemplate_vattspec_master.txt")
system = System("vattspec", template)
system.set_keyword("DEWAR", "vattspec_dewar", "Dewar name")

# ****************************************************************
# display
# ****************************************************************
display = Ds9Display()

# ****************************************************************
# read par file
# ****************************************************************
pardict = azcam.api.config.parfile_read(azcam.db.parfile)
azcam.api.config.update_pars(0, pardict["azcamserver"])

# ****************************************************************
# define names to imported into namespace when using cli
# # ****************************************************************
azcam.db.cli_cmds.update({"azcam": azcam})

# ****************************************************************
# web server
# ****************************************************************
webserver = WebServer()
azcam_exptool.load()
azcam_status.load()
azcam_webobs.load()
webserver.start()

# ****************************************************************
# azcammonitor
# ****************************************************************
monitor = AzCamMonitorInterface()
monitor.proc_path = "/azcam/azcam-vatt/bin/start_server_vattspec.bat"
monitor.register()

# ****************************************************************
# GUIs
# ****************************************************************
if 1:
    import azcam_vatt.common.start_azcamtool

# ****************************************************************
# finish
# ****************************************************************
azcam.log("Configuration complete")

# ****************************************************************
# Debug code
# ****************************************************************
if 0:
    azcam.db.verbosity = 3
    azcam.api.exposure.reset()
    # azcam.api.exposure.test(0.1, "flat")
    # input("Waiting...")
