# Author: Hannah (@github: hanphps)
# Creation: 10-Apr-2024
# Log:
#   10-Apr-2024 : Creation
#

#https://medium.com/@abdelhedihlel/upload-files-to-firebase-storage-using-python-782213060064
# Internal
from com.lib.gremlin.tools import Gremlin
from com.lib.handlers.config import ConfigHandler
from com.lib.web.database import DatabaseHandler

# External
import os
import time
import json
import firebase_admin
from firebase_admin import credentials, storage, firestore

TASK = 'pyro'

class PyroSettings:
    def __init__(self,
                 evt_hndlr : Gremlin,
                 cnf_hndlr : ConfigHandler):
        self.evt_hndlr = evt_hndlr
        self.cnf_hndlr = cnf_hndlr
        self.evt_hndlr.link_event(task=TASK,
                                  msg = 'Attempting to read pyro config')

        self.cnf = self.cnf_hndlr.get_config('pyro')
        self.cred = credentials.Certificate(self.cnf_hndlr.get_json(self.cnf['key']))

class PyroHandler:
    def __init__(self,
                 evt_hndlr : Gremlin,
                 cnf_hndlr : ConfigHandler,
                 user : str = 'dummy'):
        self.user = user
        self.evt_hndlr = evt_hndlr
        self.pyro_cnf = PyroSettings(evt_hndlr=evt_hndlr,cnf_hndlr=cnf_hndlr)

        self.evt_hndlr.link_event(task=TASK,
                                  msg = 'Attempting to init a Firebase app with storage bucket {%s.appspot.com}' % (self.pyro_cnf.cnf['bucket'])
                                )
        
        self.firebase = firebase_admin.initialize_app(self.pyro_cnf.cred,
                                                      {'storageBucket': '%s.appspot.com' % (self.pyro_cnf.cnf['bucket'])}
                                                      )
        self.bucket = self.get_storage()

        self.evt_hndlr.link_event(task=TASK,
                                  msg = 'Attempting to init a Firebase db'
                                )
        print(firestore.client(app=self.firebase))
        self.db_hndlr = DatabaseHandler(evt_hndlr= evt_hndlr, cnf = self.pyro_cnf.cnf['database'], db = firestore.client(app = self.firebase))


    def get_storage(self):
        self.evt_hndlr.link_event(task=TASK,
                                  msg = 'Attempting to retrieve Firebase storage')
        return storage.bucket(app=self.firebase)
    
    def upload(self,
               file_path : str = 'INVALID'):
        self.evt_hndlr.link_event( task = TASK,
                                    msg = 'Attempting to upload to blob {%s}' % (file_path)
                                 )
        if not os.path.exists(file_path):
            self.evt_hndlr.link_error( task = TASK,
                                        msg = 'File does not exist in specified path {%s}' % (file_path)
                                     )
        if os.path.isdir(file_path):
            for file in os.listdir(file_path):
                blob = self.bucket.blob(file_path+file)
                blob.upload_from_filename(file_path+file)
        else:
            blob = self.bucket.blob(file_path)
            blob.upload_from_filename(file_path)

    
    def download(self,
               file_path : str = 'INVALID'):
        self.evt_hndlr.link_event( task = TASK,
                                    msg = 'Attempting to download from blob {%s}' % (file_path)
                                 )
        blob = self.bucket.blob(file_path)
        blob.download_to_filename(file_path)
    
    def write_full_results(self, root_res, local_path : str):
        # Full Results TODO: Partial
        res = {}
        curr_res = root_res
        while curr_res.next != None:
            res[curr_res.n] = curr_res.to_dict()
            curr_res = curr_res.next
        res[curr_res.n] = curr_res.to_dict()

        local_file =  '%s/%s_results_%s.json'%(local_path, self.user, str(time.time()))
        with open(local_file, 'w') as res_file:
            json.dump(res,res_file)
        self.upload(file_path=local_file)
        self.db_hndlr.write_run(user = self.user, msg = local_file)

        return local_file