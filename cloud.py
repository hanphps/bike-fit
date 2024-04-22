# Author: Hannah (@github: hanphps)
# Creation: 21-Apr-2024
# Log:
#   21-Apr-2024 : Creation
#

from com.external.cloud import CloudStorageHandler
from com.external.pubsub import PubSubHandler

cred_file = 'storage/config/eng-braid-420714-91e785af3dd2.json'
pubsub_hndlr = PubSubHandler(
        cred_file = cred_file,
        project_id = 'eng-braid-420714',
        subscription_path = 'projects/eng-braid-420714/subscriptions/bikefit-sub-sub'
                               )
cld_hndlr = CloudStorageHandler(
        cred_file = cred_file,
        bucket = 'bikefit')