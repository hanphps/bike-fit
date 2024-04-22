# Author: Hannah (@github: hanphps)
# Creation: 31-Mar-2024
# Log:
#   31-Mar-2024 : Creation
#

# Internal
from com.lib.gremlin.tools import Gremlin
from com.lib.handlers.result import ResultHandler

TASK = 'bike_fit'

class ValidAngles:
    def __init__(self,
               at_6_clock : tuple = (0,0), 
               in_motion : tuple = (0,0), 
               at_3_clock : tuple = (0,0), 
               at_12_clock : tuple = (0,0)):
        self.at_6_clock = at_6_clock # Saddle height
        self.at_3_clock = at_3_clock # Setback
        self.at_12_clock = at_12_clock
        self.in_motion = in_motion

class RiderType:
    def __init__(self,
               rider_type : str,
               hip_range : ValidAngles, 
               elbow_range : ValidAngles, 
               knee_range : ValidAngles, 
               ankle_range : ValidAngles):
        self.rider_type = rider_type
        self.hip_range = hip_range
        self.knee_range = knee_range
        self.elbow_range = elbow_range
        self.ankle_range = ankle_range

class RacingFit(RiderType):
    def __init__(self):
        super().__init__(
            rider_type = 'racing',
            hip_range     = ValidAngles(in_motion = (30,55)),
            knee_range    = ValidAngles(at_6_clock=(25,35)),
            elbow_range   = ValidAngles(in_motion = (90,120)),
            ankle_range   = ValidAngles(at_6_clock = (70,80),
                                    at_12_clock = (95,105))
        )

class CasualFit(RiderType):
    def __init__(self):
        super().__init__(
            rider_type = 'casual',
            hip_range     = ValidAngles(in_motion = (55,75)),
            knee_range    = ValidAngles(at_6_clock=(35,40)),
            elbow_range   = ValidAngles(in_motion = (150,170)),
            ankle_range   = ValidAngles(at_6_clock = (70,80),
                                    at_12_clock = (95,105))
        )

class Adjustment():
    def __init__(self,
                 name : str = '',
                 needs_adjustment : bool = False,
                 adjustment_dir : int = 0):
        self.name = name
        self.needs_adjustment = needs_adjustment
        self.adjustment_dir = adjustment_dir

class BikeFitHandler:
    def __init__(self,
               evt_hndlr: Gremlin,
               res_hndlr : ResultHandler,
               fit_mode : RiderType = CasualFit()
               ):
        self.evt_hndlr = evt_hndlr
        self.res_hndlr = res_hndlr
        self.fit_mode = fit_mode
        self.averages_taken = False
        self.checked_validity = False
        self.recommended_adjustments = []
        self.given_recc = False
    
    def get_o_clock_motions(self):
        if self.res_hndlr.curr_res is not None:
            self.evt_hndlr.link_event(task=TASK,msg = 'checking positions')
            n_max = self.res_hndlr.curr_res.n + 1 # Starts at 0
            if self.res_hndlr.curr_res.n <= 4:
                self.evt_hndlr.link_error(task=TASK, msg='Not enough data points to determne fit {n=%i}' % (self.res_hndlr.curr_res.n))
            first_result = self.res_hndlr.get_root_result()
            res = first_result.next # Get n_th + 1
            while res.next != None:
                pass_check_6 = False
                pass_check_3 = False
                # Check six o clock
                if res.next.next != None and res.previous.previous != None:
                    pass_check_6 = (((res.joints.ankle.pos.y > res.next.next.joints.ankle.pos.y or res.joints.ankle.pos.y > res.next.joints.ankle.pos.y) and (res.previous.joints.ankle.pos.y < res.joints.ankle.pos.y or  res.previous.previous.joints.ankle.pos.y < res.joints.ankle.pos.y)) and # Movement is not smooth and double derivative is required for perfect minima
                                     (res.next.joints.knee.rot.angle < res.joints.knee.rot.angle and res.previous.joints.knee.rot.angle < res.joints.knee.rot.angle)) # knee extended
                    pass_check_3 = (((res.joints.ankle.pos.y < res.next.joints.ankle.pos.y and res.previous.joints.ankle.pos.y < res.joints.ankle.pos.y) or (res.joints.ankle.pos.y < res.next.next.joints.ankle.pos.y  and res.previous.previous.joints.ankle.pos.y < res.joints.ankle.pos.y)) and  # downward motion on y
                                    (res.previous.joints.ankle.rot.angle < res.joints.ankle.rot.angle) and (res.joints.ankle.rot.angle < res.next.joints.ankle.rot.angle) ) # ankle angling
                    if res.joints.left_facing_camera:
                        pass_check_6 = pass_check_6 and (res.joints.ankle.pos.x > res.next.joints.ankle.pos.x and res.previous.joints.ankle.pos.x > res.joints.ankle.pos.x)  # sideware motion on x
                        pass_check_3 = pass_check_3 and ((res.joints.ankle.pos.x > res.next.next.joints.ankle.pos.x) and (res.previous.previous.joints.ankle.pos.x < res.joints.ankle.pos.x)) # Movement is not smooth and double derivative is required for perfect minima                    else:
                    else:   
                        pass_check_6 = pass_check_6 and (res.joints.ankle.pos.x < res.next.joints.ankle.pos.x and res.previous.joints.ankle.pos.x < res.joints.ankle.pos.x) # sideware motion on x
                        pass_check_3 = pass_check_3 and ((res.joints.ankle.pos.x < res.next.next.joints.ankle.pos.x) and (res.previous.previous.joints.ankle.pos.x > res.joints.ankle.pos.x)) # Movement is not smooth and double derivative is required for perfect maxima                    else:
                
                self.res_hndlr.fit_params.hip.in_motion.angle_average += res.joints.hip.rot.angle
                self.res_hndlr.fit_params.knee.in_motion.angle_average += res.joints.knee.rot.angle
                self.res_hndlr.fit_params.elbow.in_motion.angle_average += res.joints.elbow.rot.angle

                if pass_check_6:
                    #TODO : self.evt_hndlr.link_event(task=TASK,msg = '')
                    self.res_hndlr.fit_params.hip.six_o_clock.angle_average += res.joints.hip.rot.angle
                    self.res_hndlr.fit_params.knee.six_o_clock.angle_average += res.joints.knee.rot.angle
                    self.res_hndlr.fit_params.elbow.six_o_clock.angle_average += res.joints.elbow.rot.angle
                    self.res_hndlr.fit_params.at_six_o_clock.append(res.n)
                if pass_check_3:
                    #TODO : self.evt_hndlr.link_event(task=TASK,msg = '')
                    self.res_hndlr.fit_params.hip.three_o_clock.angle_average += res.joints.hip.rot.angle
                    self.res_hndlr.fit_params.knee.three_o_clock.angle_average += res.joints.knee.rot.angle
                    self.res_hndlr.fit_params.elbow.three_o_clock.angle_average += res.joints.elbow.rot.angle
                    self.res_hndlr.fit_params.knee.three_o_clock.pos_average += res.joints.knee.pos.x
                    self.res_hndlr.fit_params.foot.three_o_clock.pos_average += res.joints.foot.pos.x
                    self.res_hndlr.fit_params.at_three_o_clock.append(res.n)

                res = res.next

            #TODO : self.evt_hndlr.link_event(task=TASK,msg = '')
            self.res_hndlr.fit_params.hip.in_motion.angle_average /= n_max
            self.res_hndlr.fit_params.knee.in_motion.angle_average /= n_max
            self.res_hndlr.fit_params.elbow.in_motion.angle_average /= n_max

            #print('TESTGOTIT'+str(len(self.res_hndlr.fit_params.at_three_o_clock))) 
            #print('TESTGOTIT'+str(len(self.res_hndlr.fit_params.at_six_o_clock))) 
            if len(self.res_hndlr.fit_params.at_three_o_clock)>0:
                #TODO : self.evt_hndlr.link_event(task=TASK,msg = '')
                
                self.res_hndlr.fit_params.hip.three_o_clock.angle_average /= len(self.res_hndlr.fit_params.at_three_o_clock)
                self.res_hndlr.fit_params.knee.three_o_clock.angle_average /=len(self.res_hndlr.fit_params.at_three_o_clock)
                self.res_hndlr.fit_params.elbow.three_o_clock.angle_average /=len(self.res_hndlr.fit_params.at_three_o_clock)
                self.res_hndlr.fit_params.knee.three_o_clock.pos_average /=len(self.res_hndlr.fit_params.at_three_o_clock)
                self.res_hndlr.fit_params.foot.three_o_clock.pos_average /=len(self.res_hndlr.fit_params.at_three_o_clock)
            else:
                
                self.evt_hndlr.link_error(task=TASK, msg='Cannot determine 3 o clock position. There are no data points in results to determine a fit')
            
            if len(self.res_hndlr.fit_params.at_six_o_clock)>0:
                #TODO : self.evt_hndlr.link_event(task=TASK,msg = '')
                self.res_hndlr.fit_params.hip.six_o_clock.angle_average /= len(self.res_hndlr.fit_params.at_six_o_clock)
                self.res_hndlr.fit_params.knee.six_o_clock.angle_average /= len(self.res_hndlr.fit_params.at_six_o_clock)
                self.res_hndlr.fit_params.elbow.six_o_clock.angle_average /= len(self.res_hndlr.fit_params.at_six_o_clock)
            else:
                self.evt_hndlr.link_error(task=TASK, msg='Cannot determine 6 o clock position. There are no data points in results to determine a fit')

            self.averages_taken = True
        else:
            self.evt_hndlr.link_error(task=TASK, msg='Current results are empty. There are no data points in results to determine a fit')
    
    def is_o_clock_valid(self):
        if not self.averages_taken:
            self.evt_hndlr.link_error(task=TASK, msg='Current results are empty. Must get motion averages before determining validity')
        # Check Elbow is OK
        self.res_hndlr.fit_params.elbow.six_o_clock.in_range= self.res_hndlr.fit_params.elbow.six_o_clock.angle_average <= self.fit_mode.elbow_range.in_motion[1] and self.res_hndlr.fit_params.elbow.six_o_clock.angle_average >= self.fit_mode.elbow_range.in_motion[0]
        self.res_hndlr.fit_params.elbow.six_o_clock.delta = 0

        # Check Hip is OK
        self.res_hndlr.fit_params.hip.six_o_clock.in_range = self.res_hndlr.fit_params.hip.six_o_clock.angle_average  <= self.fit_mode.hip_range.in_motion[1] and self.res_hndlr.fit_params.hip.six_o_clock.angle_average >= self.fit_mode.hip_range.in_motion[0]
        self.res_hndlr.fit_params.hip.six_o_clock.delta = 0
        
        # Check knee range
        self.res_hndlr.fit_params.knee.six_o_clock.in_range = (180-self.res_hndlr.fit_params.knee.six_o_clock.angle_average) <= self.fit_mode.knee_range.at_6_clock[1] and (180-self.res_hndlr.fit_params.knee.six_o_clock.angle_average) >=  self.fit_mode.knee_range.at_6_clock[0]
        self.res_hndlr.fit_params.knee.six_o_clock.delta = 0

        # In 3 o clock
        self.res_hndlr.fit_params.elbow.three_o_clock.in_range = self.res_hndlr.fit_params.elbow.three_o_clock.angle_average <= self.fit_mode.elbow_range.in_motion[1] and self.res_hndlr.fit_params.elbow.three_o_clock.angle_average >= self.fit_mode.elbow_range.in_motion[0]
        self.res_hndlr.fit_params.elbow.three_o_clock.delta = 0

        # Check Hip is OK
        self.res_hndlr.fit_params.hip.three_o_clock.in_range = self.res_hndlr.fit_params.hip.three_o_clock.angle_average<= self.fit_mode.hip_range.in_motion[1] and  self.res_hndlr.fit_params.hip.three_o_clock.angle_average>= self.fit_mode.hip_range.in_motion[0]
        self.res_hndlr.fit_params.hip.three_o_clock.delta = 0

        
        # Check knee is behind pedal stroke
        #TODO: Do check in operation
        knee_valid = False
        knee_delta = 0
        if self.res_hndlr.curr_res.joints.left_facing_camera:
            knee_valid = self.res_hndlr.fit_params.foot.three_o_clock.pos_average > self.res_hndlr.fit_params.knee.three_o_clock.pos_average
            knee_delta = self.res_hndlr.fit_params.foot.three_o_clock.pos_average - self.res_hndlr.fit_params.knee.three_o_clock.pos_average
        else:
            knee_valid = self.res_hndlr.fit_params.foot.three_o_clock.pos_average < self.res_hndlr.fit_params.knee.three_o_clock.pos_average
            knee_delta = self.res_hndlr.fit_params.foot.three_o_clock.pos_average - self.res_hndlr.fit_params.knee.three_o_clock.pos_average
        #print(knee_valid)
        self.res_hndlr.fit_params.knee.three_o_clock.in_range = knee_valid
        self.res_hndlr.fit_params.knee.three_o_clock.delta = knee_delta

        # In motion
         # Check Elbow is OK
        self.res_hndlr.fit_params.elbow.in_motion.in_range=  self.res_hndlr.fit_params.elbow.in_motion.angle_average <= self.fit_mode.elbow_range.in_motion[1] and self.res_hndlr.fit_params.elbow.in_motion.angle_average >= self.fit_mode.elbow_range.in_motion[0]
        self.res_hndlr.fit_params.elbow.in_motion.delta = 0

        # Check Hip is OK
        self.res_hndlr.fit_params.hip.in_motion.in_range = self.res_hndlr.fit_params.hip.in_motion.angle_average <= self.fit_mode.hip_range.in_motion[1] and self.res_hndlr.fit_params.hip.in_motion.angle_average >= self.fit_mode.hip_range.in_motion[0]
        self.res_hndlr.fit_params.hip.in_motion.delta = 0

        # Has performed validity check
        self.checked_validity = True
        '''print(self.res_hndlr.fit_params.hip.three_o_clock.__dict__)
        print(self.res_hndlr.fit_params.knee.three_o_clock.__dict__)
        print(self.res_hndlr.fit_params.elbow.three_o_clock.__dict__)
        print(self.res_hndlr.fit_params.foot.three_o_clock.__dict__)

        print(self.res_hndlr.fit_params.hip.six_o_clock.__dict__)
        print(self.res_hndlr.fit_params.knee.six_o_clock.__dict__)
        print(self.res_hndlr.fit_params.elbow.six_o_clock.__dict__)
        print(self.res_hndlr.fit_params.foot.six_o_clock.__dict__)

        print(self.res_hndlr.fit_params.hip.in_motion.__dict__)
        print(self.res_hndlr.fit_params.knee.in_motion.__dict__)
        print(self.res_hndlr.fit_params.elbow.in_motion.__dict__)
        print(self.res_hndlr.fit_params.foot.in_motion.__dict__)'''
    
    def do_fit(self):
        if not self.checked_validity:
            self.evt_hndlr.link_error(task=TASK, msg='Current validity results are empty. Must get motion fits validified checked before determining fit')
        if self.given_recc and len(self.recommended_adjustments) == 0:
                self.evt_hndlr.link_error(task=TASK, msg='Currrent adjustment is already perfect according to algorithm')
        self.recommended_adjustments = []

        # Seatpost
        if not self.res_hndlr.fit_params.knee.six_o_clock.in_range:
            self.recommended_adjustments.append(Adjustment(name='seat position for downward power',
                                                           needs_adjustment = True,
                                                           adjustment_dir = self.res_hndlr.fit_params.knee.six_o_clock.delta))
            
        if not self.res_hndlr.fit_params.knee.three_o_clock.in_range:
            self.recommended_adjustments.append(Adjustment(name='seat position for knee over/undershoot',
                                                           needs_adjustment = True,
                                                           adjustment_dir = self.res_hndlr.fit_params.knee.three_o_clock.delta))

        # Saddle pos
        if not self.res_hndlr.fit_params.knee.three_o_clock.in_range:
            self.recommended_adjustments.append(Adjustment(name='seat position for knee over/undershoot',
                                                           needs_adjustment = True,
                                                           adjustment_dir = self.res_hndlr.fit_params.knee.three_o_clock.delta))
        if not self.res_hndlr.fit_params.elbow.in_motion.in_range:
            self.recommended_adjustments.append(Adjustment(name='seat position adjustment for elbow motion range',
                                                           needs_adjustment = True,
                                                           adjustment_dir = self.res_hndlr.fit_params.elbow.in_motion.delta))
        # Stem
        if not self.res_hndlr.fit_params.elbow.in_motion.in_range:
            self.recommended_adjustments.append(Adjustment(name='stem adjustment for elbow motion range',
                                                           needs_adjustment = True,
                                                           adjustment_dir = self.res_hndlr.fit_params.elbow.in_motion.delta))

        # Headset
        if not self.res_hndlr.fit_params.elbow.in_motion.in_range:
            self.recommended_adjustments.append(Adjustment(name='headset for elbow motion range',
                                                           needs_adjustment = True,
                                                           adjustment_dir = self.res_hndlr.fit_params.elbow.in_motion.delta))

        self.given_recc = True