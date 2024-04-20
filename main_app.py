# Author: Hannah (@github: hanphps)
# Creation: 31-Mar-2024
# Log:
#   31-Mar-2024 : Creation
#
from com.lib.handlers.video import MediaSettings, VideoHandler
from com.lib.handlers.result import ResultHandler
from com.lib.gremlin.tools import Gremlin
from com.lib.handlers.bike import BikeFitHandler
from com.lib.handlers.config import ConfigHandler
from com.lib.web.pyro import PyroHandler
import os



TASK = 'main_task'

evt_hndlr = Gremlin(hndl='Main',
                    export_logs=('%s/storage/dat/logs/'%(os.getcwd()))
                    )
res_hndlr = ResultHandler(evt_hndlr=evt_hndlr)
cnfg_hndlr = ConfigHandler(evt_hndlr=evt_hndlr, config_path=('%s/storage/config/'%(os.getcwd())) )
print( (cnfg_hndlr.get_config('pyro')))
fb_hdnlr = PyroHandler(evt_hndlr=evt_hndlr, cnf_hndlr=cnfg_hndlr)
#fb_hdnlr.upload('storage/dat/logs/')

#TODO : evt_hndlr.log_event
settings = MediaSettings(
    model= ('%s/storage/config/tasks/pose_landmarker_heavy.task'%(os.getcwd())),
    vid_dir=('%s/storage/dat/videos/'%(os.getcwd()))
)

#TODO : evt_hndlr.log_event
vhdlr = VideoHandler(
    evt_hndlr= evt_hndlr,
    res_hndlr = res_hndlr,
    settings= settings)

vhdlr.process_video('crop-test.mp4',defined_limit=60)

#TODO : evt_hndlr.log_event
bke_fit = BikeFitHandler(
    evt_hndlr=evt_hndlr,
    res_hndlr=res_hndlr)

#TODO : evt_hndlr.log_event
bke_fit.get_o_clock_motions()
bke_fit.is_o_clock_valid()

fb_hdnlr.write_full_results(root_res = res_hndlr.get_root_result(), local_path='storage/dat/results', user = 'Tester')