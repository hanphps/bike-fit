# Author: Hannah (@github: hanphps)
# Creation: 21-Apr-2024
# Log:
#   21-Apr-2024 : Creation
#

# External
from google.cloud import pubsub_v1
from google.oauth2 import service_account

import os
import json

class PubSubHandler:

    def __init__(self,
                 cred_file : str = '',
                 project_id : str = '',
                 subscription_path : str = ''):
        self.cred_file = cred_file
        self.cred_exits()

        self.project_id = project_id
        self.subscription_path = subscription_path
        self.return_settings = {}

    def post_message_test(self, topic_path: str = '', data = {}):
        credentials = credentials = service_account.Credentials.from_service_account_file(self.cred_file)
        publisher = pubsub_v1.PublisherClient(credentials=credentials)
        data = json.dumps(data)
        data = data.encode('utf-8')
        future = publisher.publish(topic_path, data)

    def cred_exits(self):
        if os.path.exists(self.cred_file):
            return True
        else:
            raise Exception('Credential file DNE')
    
    def wait_for_event(self):

        credentials = credentials = service_account.Credentials.from_service_account_file(self.cred_file)
        subscriber = pubsub_v1.SubscriberClient(credentials = credentials)
        

        with subscriber:
            print(f"Listening for messages on {self.subscription_path}..\n")
            response = subscriber.pull(subscription = self.subscription_path, max_messages = 1, timeout = 30)
            if response.received_messages:
                self.return_settings = json.loads(response.received_messages[0].message.data.decode('utf-8'))
            subscriber.acknowledge(subscription = self.subscription_path, ack_ids=[response.received_messages[0].ack_id])

    def get_message(self):
        return self.return_settings