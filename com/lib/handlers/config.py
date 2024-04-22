# Author: Hannah (@github: hanphps)
# Creation: 31-Mar-2024
# Log:
#   31-Mar-2024 : Creation
#

# Internal
from com.lib.gremlin.tools import Gremlin

# External
import os
import yaml

TASK = 'config_manager'
END = '.yaml'
END_JSON = '.json'

class ConfigHandler:

    
    def __init__(self,
                 evt_hndlr : Gremlin,
                 config_path : str = 'INVALID'
                 ):
        self.config_path = config_path
        self.evt_hndlr = evt_hndlr

        if not os.path.isdir(self.config_path):
            self.evt_hndlr.link_error( task = TASK,
                                        msg = 'Directory does not exist in specified path {%s}' % self.config_path
                                     )
    
    def get_config(self,
                   config_name : str):
        self.evt_hndlr.link_event(task=TASK,msg = 'checking config for %s'% config_name)

        if not os.path.exists(self.config_path+config_name+END):
            self.evt_hndlr.link_error( task = TASK,
                                        msg = 'File does not exist in specified path {%s}' % (self.config_path+config_name+END)
                                     )

        self.evt_hndlr.link_event(task=TASK,msg = 'Opening config at {%s}'% (self.config_path+config_name+END))
        
        output = None
        output = yaml.safe_load(open(self.config_path+config_name+END)) 

        self.evt_hndlr.link_event(task=TASK,msg = 'Successfully opened config at {%s}'% (self.config_path+config_name+END))

        return output
        
    def get_json(self,
                 config_name : str ):
        self.evt_hndlr.link_event(task=TASK,msg = 'checking config for %s'% config_name)

        if not os.path.exists(self.config_path+config_name+END_JSON):
            self.evt_hndlr.link_error( task = TASK,
                                        msg = 'File does not exist in specified path {%s}' % (self.config_path+config_name+END_JSON)
                                     )

        self.evt_hndlr.link_event(task=TASK,msg = 'Getting json config at {%s}'% (self.config_path+config_name+END))
        
        return self.config_path+config_name+END_JSON