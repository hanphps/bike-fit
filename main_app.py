# Author: Hannah (@github: hanphps)
# Creation: 31-Mar-2024
# Log:
#   31-Mar-2024 : Creation
#   21-Apr-2024 : Add CLI input
#
from com.lib.handlers.video import MediaSettings, VideoHandler
from com.lib.handlers.result import ResultHandler
from com.lib.gremlin.tools import Gremlin
from com.lib.handlers.bike import BikeFitHandler
from com.lib.handlers.config import ConfigHandler
from com.lib.web.pyro import PyroHandler
from cloud import cld_hndlr, pubsub_hndlr

# External
import os
import sys



TASK = 'main_task'
VID_DIR = 'storage/dat/videos/'

def process_fit():
    
    pubsub_hndlr.post_message_test(
        topic_path = 'projects/eng-braid-420714/topics/bikefit-sub',
        data = {
            'user': 'Test',
            'video_path': 'crop-test.mp4',
            'record_video' : False
        }
    )
    pubsub_hndlr.wait_for_event()
    job_data = pubsub_hndlr.get_message()
    cld_hndlr.get_data_from_cloud(file_name=job_data['video_path'], move_path = VID_DIR)

    if not isinstance(job_data,dict):
        # TODO: Throw error
        pass
    if not job_data['video_path'] or not job_data['user'] or not job_data['record_video']:
        # TODO : Throw error
        pass

    evt_hndlr = Gremlin(hndl='Main',
                        user=job_data['user'],
                        export_logs='storage/dat/logs/'
                        )
    res_hndlr = ResultHandler(evt_hndlr=evt_hndlr)
    cnfg_hndlr = ConfigHandler(evt_hndlr=evt_hndlr, config_path='storage/config/')
    fb_hdnlr = PyroHandler(evt_hndlr=evt_hndlr, cnf_hndlr=cnfg_hndlr, user=job_data['user'])

    #TODO : evt_hndlr.log_event
    settings = MediaSettings(
        model= ('storage/config/tasks/pose_landmarker_heavy.task'),
        vid_dir=VID_DIR
    )

    #TODO : evt_hndlr.log_event
    vhdlr = VideoHandler(
        evt_hndlr= evt_hndlr,
        res_hndlr = res_hndlr,
        settings= settings)

    output_video = vhdlr.process_video(job_data['video_path'], record_video = job_data['record_video'])

    #TODO : evt_hndlr.log_event
    if output_video is not None:
        cld_hndlr.queue_file(output_video)


    #TODO : evt_hndlr.log_event
    bke_fit = BikeFitHandler(
        evt_hndlr=evt_hndlr,
        res_hndlr=res_hndlr)

    #TODO : evt_hndlr.log_event
    bke_fit.get_o_clock_motions()
    bke_fit.is_o_clock_valid()

    results_file = fb_hdnlr.write_full_results(root_res = res_hndlr.get_root_result(), local_path='storage/dat/results', user = job_data['user'])
    
    #TODO : evt_hndlr.log_event
    if results_file is not None:
        cld_hndlr.queue_file(file_name = results_file)

    cld_hndlr.move_files_to_storage()

process_fit()