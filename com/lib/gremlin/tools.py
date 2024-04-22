# Author: Hannah (@github: hanphps)
# Creation: 31-Mar-2024
# Log:
#   31-Mar-2024 : Creation
#   01-Apr-2024 : Refactor + Add logging
#

# External
import time
import os

TASK = 'gremlin'
gremlin_path = '.gremlin' # Desired path can be .txt

class Event:

    def __init__(self,
                 task : str,
                 msg : str,
                 blocking : bool = False):
        
        self.task = task
        self.msg = msg
        self.timestamp = time.time()
        self.blocking = blocking

        # Doubly linked for accessibility
        self.previous = None
        self.next = None

class Gremlin:
    def __init__(self, 
                 hndl : str = 'dummy',
                 user : str = 'dummy',
                 export_logs : str = './'):
        ''' 
            NOTE:
                Python reuses memory of declared classes that are exactly alike. 
                In case of multiple handlers, a unique handle id (hndl) is require
        '''
        self.hndl = hndl
        self.user = user
        self.export_logs = export_logs
        self.curr_log = '%s%s_log_%s%s'%(export_logs,self.user,str(time.time_ns()),gremlin_path)
        self.curr_err_log = '%s%s_error_%s%s'%(export_logs,self.user,str(time.time_ns()),gremlin_path)
        self.curr_evt = None
    
    def link_event(self,
                   task : str = 'unknown',
                   msg : str = 'unknown',
                   blocking : bool = False):
        
        warning = '(%s) > [EVENT]: Linking event (task = {%s}, msg = {%s}, blocking = {%s})' % (time.time(),task,msg,blocking)
        print(warning)
        self.add_to_evt_log(msg=warning)
        evt = Event(task=task, msg=msg, blocking=blocking)
        if evt is not None:
            if self.curr_evt is not None:
                if self.curr_evt.next == None:
                    evt.previous = self.curr_evt
                    self.curr_evt.next = evt
                    self.curr_evt = self.curr_evt.next
                else:
                    curr_evt = self.curr_evt
                    while curr_evt.next is not None:
                        curr_evt = curr_evt.next
                    
                    curr_evt.next = evt
                    self.curr_evt = curr_evt.nxt
            else:
                self.curr_evt = evt
            
            if evt.blocking :
                self.hndl_error(self.curr_evt)
        else:
            raise Exception('Event does not exist!')

    def link_error(self,
                   task : str = 'unknown',
                   msg : str = 'unknown'):
        self.link_event(task=task, msg=msg, blocking=True)
        

    def hndl_error(self,
                   evt: Event):
        warning = '(%s) > [EVENT]: Handling error event (task = {%s}, msg = {%s}, blocking = {%s})' % (time.time(),evt.task,evt.msg,evt.blocking)
        print(warning)
        self.add_to_evt_log(msg=warning)
        has_blocking        = False
        first_blocking      = None
        if evt is not None:
            curr_evt = evt
            while curr_evt.previous is not None:
                # TODO: callback events
                #if curr_evt.callback is not None:
                #        curr_evt.callback()
                warning = '(%s) > [EVENT]: Previous event (task = {%s}, msg = {%s}, blocking = {%s})' % (time.time(),curr_evt.task,curr_evt.msg,curr_evt.blocking)
                print(warning)
                self.add_to_evt_log(msg=warning)
                if curr_evt.blocking and not has_blocking:
                    # This should be root error however it can be blocked because of previous unknown issues
                    has_blocking = True
                    first_blocking = curr_evt

                curr_evt = curr_evt.previous
            
            # TODO: callback events
            #if curr_evt.callback is not None:
            #        curr_evt.callback()
            
            warning = '(%s) > [EVENT]: Previous event (task = {%s}, msg = {%s}, blocking = {%s})' % (time.time(),curr_evt.task,curr_evt.msg,curr_evt.blocking)
            print(warning)
            self.add_to_evt_log(msg=warning)
            # Raise first blocking error
            if has_blocking:
                warning = '(%s) > [ROOT ERROR]: Exception raised! (task = {%s}, msg = {%s}, blocking = {%s})' % (time.time(),curr_evt.task,curr_evt.msg,curr_evt.blocking)
                self.add_to_evt_log(msg=warning)
                self.dump_evt_log()
                raise Exception(first_blocking.msg)
            self.curr_evt = None
        else:
            raise Exception('Event does not exist!')

    def get_root_event(self):
        self.link_event( task = TASK, msg = 'getting root event')
        if self.curr_evt is not None:
            curr_evt = self.curr_evt
            while curr_evt.previous is not None:
                curr_evt = curr_evt.previous
            return curr_evt
        else:
            self.link_error(task = TASK, msg = 'getting root event not possible. Event does not exist')

    def add_to_err_log(self,msg):
        if self.export_logs is not None and os.path.isdir(self.export_logs):
            if os.path.exists(self.curr_err_log):
                with open(self.curr_err_log,'a') as file:
                    file.write('%s%s'%(str(msg),'\n'))
            else:
                with open(self.curr_err_log,'w') as file:
                    file.write(' GREMLIN ERROR LOG START \n')
                    file.write('%s%s'%(str(msg),'\n'))
        else:
            raise Exception('export log path does not exist at {%s}' % (self.export_logs))
    def add_to_evt_log(self,msg):
        if self.export_logs is not None and os.path.isdir(self.export_logs):
            if os.path.exists(self.curr_log):
                with open(self.curr_log,'a') as file:
                    file.write('%s%s'%(str(msg),'\n'))
            else:
                with open(self.curr_log,'w') as file:
                    file.write(' GREMLIN LOG START \n')
                    file.write('%s%s'%(str(msg),'\n'))
        else:
            raise Exception('export log path does not exist at {%s}' % (self.export_logs))
    
    def dump_evt_log(self):
        if self.export_logs is not None and os.path.isdir(self.export_logs):
            if self.curr_evt is not None:
                warning = '(%s) > [DUMPING LOGS]: Last event (task = {%s}, msg = {%s}, blocking = {%s})' % (time.time(),self.curr_evt.task,self.curr_evt.msg,self.curr_evt.blocking)
                self.add_to_err_log(msg = warning)
                root_evt = self.get_root_event()
                if root_evt is not None:
                    curr_evt = root_evt
                    while curr_evt.next is not None:
                        self.add_to_err_log(msg=str(curr_evt.__dict__))
                        curr_evt = curr_evt.next
                    self.add_to_err_log(msg=str(curr_evt.__dict__))
                else:
                    self.link_error(task = TASK, msg = 'Unable to find a root error!') # Really odd case?'''
            else:
                self.link_error(task = TASK, msg = 'no events exist to dump!')
        else:
            raise Exception('export log path does not exist at {%s}' % (self.export_logs))