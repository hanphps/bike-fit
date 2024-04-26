from cloud import pubsub_hndlr
import requests
import json
pubsub_hndlr.post_message_test(
        topic_path = 'projects/eng-braid-420714/topics/bikefit-sub',
        data = {
            "user": 'Test@morningbyt.es',
            "video_path": 'crop-test.mp4',
            "record_video" : False
        }
    )