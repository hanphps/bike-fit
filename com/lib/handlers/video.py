# Author: Hannah (@github: hanphps)
# Creation: 10-Apr-2024
# Log:
#   10-Apr-2024 : Creation
#

# Internal
from com.lib.gremlin.tools import Gremlin
from com.lib.handlers.result import ResultHandler
from com.lib.handlers.body import BodyData, Joint

# External
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import cv2
from numpy import ndarray
import os


TASK = 'video_handler'
class MediaSettings:

    def __init__(self,
                 model : str = '',
                 accuracy : float = 0.75,
                 vid_dir : str = ''):
        self.model = model
        self.min_accuracy = accuracy
        self.vid_dir = vid_dir
        

class VideoHandler:
    
    def __init__(self,
                 evt_hndlr : Gremlin,
                 res_hndlr : ResultHandler,
                 settings : MediaSettings = None
                 ):
        self.settings = settings
        self.landmarker = None
        self.evt_hndlr = evt_hndlr
        self.res_hndlr= res_hndlr
        

    def create_landmarker(self):
        self.evt_hndlr.link_event( task = TASK,
                                    msg = 'creating landmarker'
                                  )
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        if not os.path.exists(self.settings.model):
            self.evt_hndlr.link_error( task = TASK,
                                    msg = 'landmarker model does not exist in specified path {%s}' % self.settings.model
                                  )

        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.settings.model),
            running_mode=VisionRunningMode.VIDEO,
            min_pose_detection_confidence = self.settings.min_accuracy,
            min_tracking_confidence = self.settings.min_accuracy,
            min_pose_presence_confidence = self.settings.min_accuracy)
        
        self.landmarker = PoseLandmarker.create_from_options(options)

    def draw_analytics_on_image(self,
                       img : ndarray):
        self.evt_hndlr.link_event( task = TASK,
                                    msg = 'drawing analytics on video'
                                  )
        # Draw angles
        if self.res_hndlr.curr_res is not None:
            curr_res = self.res_hndlr.curr_res
            if curr_res.joints is not None:
                img = cv2.putText(img, 'timestamp:' +str(self.res_hndlr.curr_res.timestamp),
                       (0,img.shape[0]),
                       cv2.FONT_HERSHEY_SIMPLEX, .5, (57, 255, 20), 1, cv2.LINE_AA
                            )
                attributes = list(curr_res.joints.__dict__.values())
                for attr in attributes:
                    if isinstance(attr,Joint):
                        if attr.rot is not None:
                            coord = attr.get_real_coord(width = img.shape[1], height =img.shape[0])
                            # Draw joint
                            img = cv2.circle(img,
                                                coord,
                                                10,
                                                (57, 255, 0),
                                                -1)
                            # Visualize angle
                            offset_x = int(.01*img.shape[1])
                            img = cv2.putText(img, '%s : %f'%(attr.name , round(attr.rot.angle,2)),
                                        (coord[0]+offset_x,coord[1]),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (57, 255, 20), 1, cv2.LINE_AA
                                                )
            else:
                self.evt_hndlr.link_error( task = TASK,
                                    msg = 'joint data does not exist for result {n = %i}' % curr_res.n
                                  )
        else:
            self.evt_hndlr.link_error( task = TASK,
                                    msg = 'Result does not exist for analytics'
                                  )
        return img

    def process_video(self,
                      vid_path : str = '', 
                      defined_limit : int = None,
                      record_video : bool = False):
        self.evt_hndlr.link_event( task = TASK,
                                    msg = 'processing video in specified path {%s}' % (self.settings.vid_dir+vid_path)
                                  )
        # Create landmarker
        if self.landmarker == None:
            self.create_landmarker()

        # Load video
        print(self.settings.vid_dir+vid_path)
        if not os.path.exists(self.settings.vid_dir+vid_path):
            self.evt_hndlr.link_error( task = TASK,
                                    msg = 'video does not exist in specified path {%s}' % (self.settings.vid_dir+vid_path)
                                  )
            
        cap = cv2.VideoCapture(self.settings.vid_dir+vid_path)

        # Prep video recording
        if record_video:
            self.evt_hndlr.link_event( task = TASK,
                                    msg = 'preping to record video'
                                  )
            # Configure output video properties
            codec = cv2.VideoWriter_fourcc(*'mp4v')
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Set to 0 to use the same width as the input video
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Set to 0 to use the same height as the input video
            fps = int(cap.get(cv2.CAP_PROP_FPS))  # Set the desired output frame rate

            output_path = self.settings.vid_dir+'edited_'+vid_path
            cap_writer = cv2.VideoWriter(output_path, codec, fps, (frame_width, frame_height))

        continue_while = True

        if defined_limit is not None:
            n = 0
            self.evt_hndlr.link_event( task = TASK,
                                    msg = 'processing video a cropped video with defined_limit = {%i}' % defined_limit
                                  )
            

        while continue_while:
            if defined_limit is not None:
                self.evt_hndlr.link_event( task = TASK,
                                    msg = 'processing video a cropped video with defined_limit, frame n = {%i}' % n
                                  )
            is_valid, frame = cap.read()
            if not is_valid:
                '''self.evt_hndlr.link_error( task = TASK,
                                    msg = 'video capture is not returning valid frames.'
                                  )'''
                break
            
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data = frame)
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
            results = self.landmarker.detect_for_video(mp_image,mp.Timestamp.from_seconds(timestamp).microseconds())
            
            # Link results
            self.res_hndlr.link_result(timestamp= timestamp,
                                     joints=BodyData(pose_results = results, evt_hndlr=self.evt_hndlr),
                                     frame = frame)

            if record_video:
                img = mp_image.numpy_view()
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                img = self.draw_analytics_on_image(img)
                cap_writer.write(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            if defined_limit is not None:
                n += 1
                continue_while = n<defined_limit
            else:
                continue_while = cap.isOpened()

        if record_video:
            cap_writer.release()
        cap.release()

        if record_video:
            return output_path