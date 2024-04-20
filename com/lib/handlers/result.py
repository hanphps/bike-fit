# Author: Hannah (@github: hanphps)
# Creation: 31-Mar-2024
# Log:
#   31-Mar-2024 : Creation
#

# Internal 
from com.lib.gremlin.tools import Gremlin
from com.lib.handlers.body import BodyData

# Externl
from numpy import ndarray

TASK = 'result_manager'

class FitStatus:
    def __init__(self,
                 name : str,
                 in_range : bool = False):
        self.name = name # Need valid name or python reuses place in memory
        self.in_range = in_range
        self.delta = 0
        self.angle_average = 0
        self.pos_average = 0
    
class FitJoint:
    def __init__(self,
                 name : str):
        self.name = name # Need valid name or python reuses place in memory
        self.six_o_clock = FitStatus(name = name+'_six_o_clock') 
        self.three_o_clock = FitStatus(name = name+'_three_o_clock') 
        self.in_motion = FitStatus(name = name+'_in_motion') 

class FitParameters:
    def __init__(self,
                 knee : FitJoint = FitJoint(name='knee'),
                 hip : FitJoint = FitJoint(name='hip'),
                 elbow: FitJoint = FitJoint(name='elbow'),
                 foot: FitJoint = FitJoint(name='foot'),
                 at_six_o_clock : list = [],
                 at_three_o_clock: list = []):
        self.knee = knee
        self.hip = hip
        self.elbow = elbow
        self.foot = foot
        self.at_six_o_clock = at_six_o_clock
        self.at_three_o_clock = at_three_o_clock

class Result:

    def __init__(self, 
                 joints : BodyData,
                 timestamp : float = 0.0,
                 frame : ndarray = None):
        self.n = 0 # Testing
        self.timestamp = timestamp
        self.joints = joints
        self.frame = frame

        # Doubly linked list for accessibility
        self.previous = None
        self.next = None
    def to_dict(self):
        # TODO: iterate through
        return {'n' : self.n,
                'timestamp': self.timestamp,
                'joints' : self.joints.to_dict()}

class ResultHandler:

    def __init__(self,
                 evt_hndlr: Gremlin,
                 result : Result = None,
                 fit_params: FitParameters = FitParameters()):
        
        self.curr_res = result
        self.fit_params = fit_params
        self.evt_hndlr = evt_hndlr
        
    def link_result(self,
                    joints : BodyData,
                    timestamp : float = 0.0,
                    frame : ndarray = None):
        self.evt_hndlr.link_event( task = TASK,
                                    msg = 'linking result'
                                  )
        res = Result(joints=joints,
                    timestamp= timestamp,
                    frame = frame)
        if res is not None:
            if self.curr_res != None:
                if self.curr_res.next == None:
                    res.n = self.curr_res.n + 1
                    res.previous = self.curr_res
                    self.curr_res.next = res
                    self.curr_res = self.curr_res.next
                else:
                    curr_res = self.curr_res
                    while curr_res.next != None:
                        curr_res = curr_res.next
                    res.n = curr_res.n + 1
                    curr_res.next = res
                    self.curr_res = curr_res.next
            else:
                res.n = 0
                self.curr_res = res
        else:
            self.evt_hndlr.link_error(task = TASK, msg = 'linking result does not exist')
    
    def get_root_result(self):
        self.evt_hndlr.link_event( task = TASK,
                                    msg = 'getting root result'
                                  )
        if (self.curr_res is not None):
            curr_res = self.curr_res
            while curr_res.previous != None:
                curr_res = curr_res.previous
            return  curr_res
        else:
            self.evt_hndlr.link_error(task = TASK, msg = 'getting root result not possible. result does not exist')
