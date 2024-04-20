# Author: Hannah (@github: hanphps)
# Creation: 10-Apr-2024
# Log:
#   10-Apr-2024 : Creation
#

#https://medium.com/@abdelhedihlel/upload-files-to-firebase-storage-using-python-782213060064
# Internal
from com.lib.gremlin.tools import Gremlin
from google.cloud.firestore_v1.client import Client
# External
import time

TASK = 'database'
class Entry:
    def __init__(self,
                 user : str = '',
                 entry_type : str = '',
                 msg : str = '',
                 success : bool = True
                ):
        self.user = user
        self.timestamp = time.time()
        self.entry_type = entry_type
        self.msg = msg
        self.success = success

class DatabaseHandler:

    def __init__(self,
                  evt_hndlr : Gremlin,
                  cnf : dict,
                  db: Client):
        self.evt_hndlr = evt_hndlr
        self.cnf = cnf
        self.db = db
        
    
    def write(self, 
              entry_type : str = 'INVALID',
              entry : Entry = Entry()):
        
        self.evt_hndlr.link_event(task=TASK,
                                  msg = 'Attempting to write entry to firebase database {user = %s , timestamp = %s, msg = %s, success = %s}' % (entry.user, str(entry.timestamp), entry.msg, str(entry.success))
                                )
        ref = self.db.collection(entry_type).document(str(entry.timestamp))
        ref.set(entry.__dict__, merge = True)

    def write_event(self, task : str , msg: str, success : bool = True ):
        entry = Entry(user = task,
                      entry_type =self.cnf['events'],
                      msg = msg,
                      success= success)
        self.write(entry_type= self.cnf['events'],
                   entry=entry)
    def write_error(self, task : str , msg: str ):
        self.write_event(task = task , msg = msg,  success= False)
    
    def write_run(self, user : str , msg: str, success : bool = True ):
        entry = Entry(user = user,
                      entry_type =self.cnf['runs'],
                      msg = msg,
                      success= success)
        self.write(entry_type= self.cnf['runs'],
                   entry=entry)