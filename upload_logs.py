# Author: Hannah (@github: hanphps)
# Creation: 21-Apr-2024
# Log:
#   21-Apr-2024 : Creation
#

# External
import os
from cloud import cld_hndlr

print('Uploading logs...')
for log in os.listdir('storage/dat/logs'):
    print('Uploading log {%s}' % (log))
    cld_hndlr.queue_file(file_name = 'storage/dat/logs/%s'%(log))
    cld_hndlr.move_files_to_storage()