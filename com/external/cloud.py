# Author: Hannah (@github: hanphps)
# Creation: 21-Apr-2024
# Log:
#   21-Apr-2024 : Creation
#

# External
import os
import json
from google.cloud import storage
from google.oauth2 import service_account

class CloudUpload:
    def __init__(self,
                 file_name : 'str' = ''):
        self.file_name = file_name
class CloudStorageHandler:

    def __init__(self,
                 cred_file: str = '',
                 bucket : str = ''):

        self.cred_file = cred_file
        self.bucket = bucket
        self.cred_exits()
        credentials = credentials = service_account.Credentials.from_service_account_file(self.cred_file)
        self.client = storage.Client(credentials=credentials)
        self.queued_files = []

    def cred_exits(self):
        if os.path.exists(self.cred_file):
            return True
        else:
            raise Exception('Credential file DNE')

    def get_data_from_cloud(self,
                            file_name : str = '',
                            move_path : str):
        
        blobs = self.client.list_blobs(self.bucket)
        for blob in blobs:
            if blob.name.endswith(file_name):
                print('Found file with name {%s}'%{blob.name})
                if move_path:
                    path = move_path+file_name 
                    print('Moving file from different location {from = %s, to = %s}'%{path})
                    blob.download_to_filename(path)
                else:

                    blob.download_to_filename(blob.name)
                
    
    def queue_file(self,
                   file_name: str = ''):
        self.queued_files.append(CloudUpload(file_name = file_name))
        

    def move_files_to_storage(self):
        if self.queued_files == []:
            print('No files to upload')
            return
        bucket = self.client.get_bucket(self.bucket)
        
        for file in self.queued_files:
            if isinstance(file,CloudUpload): # Check if illegally queued
                blob = bucket.blob(file.file_name)
                blob.upload_from_filename(file.file_name)



