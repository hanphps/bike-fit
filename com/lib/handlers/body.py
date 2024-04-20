# Author: Hannah (@github: hanphps)
# Creation: 31-Mar-2024
# Log:
#   31-Mar-2024 : Creation
#

# Internal
from com.lib.gremlin.tools import Gremlin

# External
import mediapipe as mp
import numpy as np
import math


# Types
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
PoseLandmark = mp.solutions.pose.PoseLandmark
NormalizedLandmark = mp.tasks.components.containers.NormalizedLandmark
        
TASK = 'body_data'
class Measurement:
    def __init__(self,
                 result : NormalizedLandmark):
        self.x = result.x
        self.y = result.y
    def to_dict(self):
        # TODO: do better
        return {'x' : self.x,
                'y' : self.y}
    def __call__(self) -> tuple:
        return (self.x,self.y)

class RotationalMeasurement:
    def __init__(self,
                 top_joint : tuple,
                 center_joint: tuple,
                 bottom_joint: tuple):
        self.angle = 0.0
        self.a = np.asarray(top_joint)
        self.b = np.asarray(center_joint)
        self.c = np.asarray(bottom_joint)

        self._calculate()
    def to_dict(self):
        # TODO: do better
        return {'angle' : self.angle}
    
    def _calculate(self):
        # Link to top error handler
        radians = np.arctan2(np.linalg.norm(np.cross(self.a-self.b, self.c-self.b)), np.dot(self.a-self.b, self.c-self.b))
        self.angle = np.abs(radians*180.0/np.pi)

        if self.angle > 180.0:
            self.angle = 360 - self.angle
        
class Joint:
    def __init__(self,
                 name : 'str',
                 pos : Measurement,
                 rot : RotationalMeasurement = None):
        self.name = name
        self.pos = pos
        self.rot = rot

    def to_dict(self):
        # TODO: do better
        if self.rot is not None:

            return {'name': self.name,
                    'pos' : self.pos.to_dict(),
                    'rot' : self.rot.to_dict()}
        else:
            return {'name': self.name,
                    'pos' : self.pos.to_dict()}
    
    def get_real_coord(self,width,height):
        # Checks if the float value is between 0 and 1.
        def is_valid_normalized_value(value: float):
            return (value > 0 or math.isclose(0, value)) and (value < 1 or
                                                            math.isclose(1, value))

        if not (is_valid_normalized_value(self.pos.x) and
                is_valid_normalized_value(self.pos.y)):
            # TODO: Draw coordinates even if it's outside of the image bounds.
            return None
        x = min(math.floor(self.pos.x * width), width - 1)
        y = min(math.floor(self.pos.y * height), height - 1)
        return (x, y)


class BodyData:

    def __init__(self,
                 pose_results : PoseLandmarkerResult,
                 evt_hndlr : Gremlin):
        
        self.evt_hndlr = evt_hndlr
        self.results = pose_results
        self.nose = None #Joint( pos = nose )
        self.shoulder =  None #Joint( pos = shoulder, rot = RotationalMeasurement(hip,shoulder,elbow))
        self.elbow = None #Joint( pos = elbow, rot = RotationalMeasurement(shoulder,elbow,wrist))
        self.wrist = None # Joint( pos = wrist, rot = RotationalMeasurement(elbow,wrist,hand))
        self.hip =  None #Joint( pos = hip, rot = RotationalMeasurement(shoulder,elbow,wrist))
        self.knee = None # Joint( pos = elbow, rot = RotationalMeasurement(ankle,knee,hip))
        self.ankle = None # Joint( pos = elbow, rot = RotationalMeasurement(knee,ankle,foot))
        self.hand = None #Joint( pos = hand )
        self.foot = None # Joint( pos = foot )

        shoulder,elbow,wrist,hip,knee,ankle,hand,foot,nose = self.get_measurements_from_results()
        self.get_bodydata_from_measurements(shoulder,elbow,wrist,hip,knee,ankle,hand,foot,nose)
        

        self.left_facing_camera = self._get_direction()
    
    def to_dict(self):
        # TODO: do better
        return {'nose': self.nose.to_dict(),
                'shoulder' : self.shoulder.to_dict(),
                'elbow': self.elbow.to_dict(),
                'wrist': self.wrist.to_dict(),
                'hip' : self.hip.to_dict(),
                'knee' : self.knee.to_dict(),
                'ankle' : self.ankle.to_dict(),
                'hand' : self.ankle.to_dict(),
                'foot' : self.foot.to_dict(),
                'left_facing_camera': self.left_facing_camera}

    def get_measurements_from_results(self,
                                  results : PoseLandmarkerResult = None):
        if self.results is None and results is not None:
            self.results = results
        if self.results is not None:
            print(len(self.results.pose_landmarks))
            if len(self.results.pose_landmarks) < 1:
                self.evt_hndlr.link_error(task=TASK,msg='pose_landmarks is less than 1. Possible results were not able to fit model')
            landmarks = self.results.pose_landmarks[0] # Need to check this
            is_left_facing = self._get_direction()
            nose = Measurement(landmarks[PoseLandmark.NOSE.value])
            if is_left_facing:
                shoulder = Measurement(landmarks[PoseLandmark.RIGHT_SHOULDER.value])
                elbow = Measurement(landmarks[PoseLandmark.RIGHT_ELBOW.value])
                wrist = Measurement(landmarks[PoseLandmark.RIGHT_WRIST.value])
                hip = Measurement(landmarks[PoseLandmark.RIGHT_HIP.value])
                knee = Measurement(landmarks[PoseLandmark.RIGHT_KNEE.value])
                ankle = Measurement(landmarks[PoseLandmark.RIGHT_ANKLE.value])
                hand = Measurement(landmarks[PoseLandmark.RIGHT_INDEX.value])
                foot = Measurement(landmarks[PoseLandmark.RIGHT_FOOT_INDEX.value])
            else:
                shoulder = Measurement(landmarks[PoseLandmark.LEFT_SHOULDER.value])
                elbow = Measurement(landmarks[PoseLandmark.LEFT_ELBOW.value])
                wrist = Measurement(landmarks[PoseLandmark.LEFT_WRIST.value])
                hip = Measurement(landmarks[PoseLandmark.LEFT_HIP.value])
                knee = Measurement(landmarks[PoseLandmark.LEFT_KNEE.value])
                ankle = Measurement(landmarks[PoseLandmark.LEFT_ANKLE.value])
                hand = Measurement(landmarks[PoseLandmark.LEFT_INDEX.value])
                foot = Measurement(landmarks[PoseLandmark.LEFT_FOOT_INDEX.value])
                
            return shoulder,elbow,wrist,hip,knee,ankle,hand,foot,nose

    def get_bodydata_from_measurements(self,
                                        shoulder : Measurement,
                                        elbow : Measurement,
                                        wrist : Measurement,
                                        hip : Measurement,
                                        knee : Measurement,
                                        ankle : Measurement,
                                        hand : Measurement,
                                        foot : Measurement,
                                        nose : Measurement):
        self.nose = Joint( name = 'nose', pos = nose )
        self.shoulder =  Joint( name = 'shoulder', pos = shoulder, rot = RotationalMeasurement(hip(),shoulder(),elbow()))
        self.elbow = Joint( name = 'elbow', 
                            pos = elbow, 
                            rot = RotationalMeasurement(shoulder(),elbow(),wrist()),
                            )
        self.wrist = Joint(name = 'wrist', pos = wrist)
        self.hip =  Joint( name = 'hip',pos = hip, rot = RotationalMeasurement(knee(),hip(),shoulder()))
        self.knee = Joint(name = 'knee', pos = knee, rot = RotationalMeasurement(ankle(),knee(),hip()))
        self.ankle = Joint(name ='ankle', pos = ankle, rot = RotationalMeasurement(knee(),ankle(),foot()))
        self.hand = Joint(name ='hand', pos = hand )
        self.foot = Joint(name ='foot', pos = foot )
        
    def _get_direction(self):
        if self.nose is not None and self.hip is not None:
            return self.nose.pos.x - self.hip.pos.x > 0
        else:
            if self.results is not None:
                if len(self.results.pose_landmarks) < 1:
                    self.evt_hndlr.link_error(task=TASK,msg='pose_landmarks is less than 1. Possible results were not able to fit model')
                landmarks = self.results.pose_landmarks[0] # Need to check this
                return landmarks[PoseLandmark.NOSE.value].x - landmarks[PoseLandmark.RIGHT_HIP.value].x > 0
            # TODO : Error handling
            pass
